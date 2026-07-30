import asyncio
import logging
import re

from .agents.schemas import CANONICAL_CHANNELS


class GenerationCancelled(Exception):
    """Levantada quando o usuário cancela uma geração de material em andamento."""


def cancel_cache_key(onboarding_id: int) -> str:
    return f'onb:cancel-gen:{onboarding_id}'


def arm_reconcile(delay_minutes: int | None = None):
    """(Re)agenda UMA rodada de reconcile_recordings via django-q (ONCE).

    Substitui o Schedule perpétuo: a fila só é varrida quando há job pendente.
    `update_or_create` por nome coalesce múltiplos webhooks/re-arms numa única
    rodada agendada (evita duplicar). ONCE + repeats=-1 → django-q deleta o
    Schedule após disparar (scheduler.py), então a cadeia para sozinha quando a
    fila drena. Idle = zero task no worker.
    """
    from datetime import timedelta
    from decouple import config
    from django.utils import timezone
    from django_q.models import Schedule

    if delay_minutes is None:
        delay_minutes = config('RECORDING_JOB_POLL_MIN', cast=int, default=60)
    Schedule.objects.update_or_create(
        name='reconcile_recordings',
        defaults={
            'func': 'onboarding.tasks.reconcile_recordings',
            'schedule_type': Schedule.ONCE,
            'next_run': timezone.now() + timedelta(minutes=delay_minutes),
            'repeats': -1,
        },
    )


def reconcile_recordings():
    """Processa RecordingJobs pendentes: acha a gravação no Drive do assessor e
    move pra pasta do cliente. Disparado on-demand pelo webhook (arm_reconcile) e
    se re-agenda enquanto sobrar job pendente.

    Idempotente e restart-safe: cada tentativa é curta. Gravação do Meet demora
    minutos a aparecer, então só varre jobs com idade ≥ RECORDING_JOB_MIN_AGE_MIN
    (evita chamadas ao Drive garantidamente vazias) e re-tenta até achar ou estourar
    RECORDING_JOB_TIMEOUT_MIN.
    """
    import logging
    from datetime import timedelta
    from decouple import config
    from django.utils import timezone
    from .models import RecordingJob
    from . import google_services, pipedrive_services

    log = logging.getLogger(__name__)
    now = timezone.now()
    # Sem pressa: gravação longa (1-4h) processa em horas; arquivar no dia seguinte
    # é aceitável. Timeout 48h cobre folga; checa de hora em hora.
    timeout_min = config('RECORDING_JOB_TIMEOUT_MIN', cast=int, default=2880)
    min_age_min = config('RECORDING_JOB_MIN_AGE_MIN', cast=int, default=30)
    deadline = now - timedelta(minutes=timeout_min)
    ready_before = now - timedelta(minutes=min_age_min)

    # Só jobs maduros: gravação do Meet não aparece nos primeiros minutos.
    for job in RecordingJob.objects.filter(
        status=RecordingJob.Status.PENDING, created_at__lte=ready_before
    ):
        job.attempts += 1
        try:
            file_id = google_services.find_recording(job.owner_google_email, job.meet_code)
            if file_id:
                google_services.move_file(job.owner_google_email, file_id, job.dest_folder_id)
                job.file_id = file_id
                job.status = RecordingJob.Status.DONE
                job.error = ''
                log.info(f'[reconcile] moved file={file_id} deal={job.deal_id}')
                _notify(pipedrive_services, job.deal_id, 'Gravação da reunião arquivada na pasta do cliente.')
            elif job.created_at < deadline:
                job.status = RecordingJob.Status.FAILED
                job.error = f'Gravação não encontrada após {timeout_min}min'
                log.warning(f'[reconcile] timeout deal={job.deal_id} meet={job.meet_code}')
                _notify(pipedrive_services, job.deal_id, f'⚠ Não localizei a gravação da reunião (Meet {job.meet_code}) após {timeout_min}min.')
            # senão: continua pending, re-tenta na próxima rodada
        except Exception as e:
            job.error = str(e)
            if job.created_at < deadline:
                job.status = RecordingJob.Status.FAILED
            log.exception(f'[reconcile] erro job={job.id}: {e}')
        job.save()

    # Re-arma enquanto sobrar qualquer pendente (inclui jobs ainda jovens, abaixo
    # do min_age). Sem pendente → nada agendado → worker em silêncio.
    if RecordingJob.objects.filter(status=RecordingJob.Status.PENDING).exists():
        arm_reconcile()


def _notify(pipedrive_services, deal_id: int, content: str):
    try:
        pipedrive_services.create_note(deal_id, content)
    except Exception:
        pass


def index_knowledge_task(names):
    """Indexação em massa do knowledge (django-q). Cada doc = S3 GET + embedding OpenAI,
    por isso é assíncrono. Falha de um não derruba os outros."""
    import logging

    from .knowledge_api import _index_one

    log = logging.getLogger(__name__)
    ok = 0
    for name in names:
        try:
            _index_one(name)
            ok += 1
        except Exception as e:
            log.warning(f'[index_kb] {name} falhou: {e}')
    log.info(f'[index_kb] indexados {ok}/{len(names)}')


def prewarm_assistant_task(material_id: int):
    """Popula cache OpenAI das 3 seções do assistant. Não bloqueia uso da IA — só acelera primeira call."""
    import logging
    import time
    from .models import GeneratedMaterial
    from .agents.assistant import AssistantSession

    log = logging.getLogger(__name__)
    t0 = time.time()
    log.info(f'[prewarm] start material_id={material_id}')
    try:
        material = GeneratedMaterial.objects.get(id=material_id)
        for section in ('crm', 'closing', 'qualification'):
            ts = time.time()
            session = AssistantSession(material=material, section=section, focus=None)
            agent = session.build_warm_agent()
            try:
                agent.run('Responda apenas: ok')
                log.info(f'[prewarm] section={section} ok ({time.time()-ts:.1f}s)')
            except Exception as e:
                log.warning(f'[prewarm] section={section} failed: {e}')
        log.info(f'[prewarm] DONE ({time.time()-t0:.1f}s) material_id={material_id}')
    except Exception as e:
        log.exception(f'[prewarm] FAILED material_id={material_id}: {e}')


# Rótulos que o modelo às vezes prefixa no texto da mensagem (devem sair do `message`).
_MSG_LABEL_RE = re.compile(r'^\s*(?:script final|script sugerido|script|mensagem)\s*:\s*', re.IGNORECASE)


# Postgres jsonb/text NÃO armazena U+0000 (NUL) — o modelo às vezes injeta NUL no meio
# de uma string e o save() estoura `unsupported Unicode escape sequence`. Tira NUL + demais
# control chars C0 (exceto \t \n \r), DEL e C1 de toda string, recursivamente.
# DEL/C1 (\x7f-\x9f): gpt-5.4-nano às vezes emite \x7f no lugar de acento → vira tofu no PDF.
# Rede de segurança caso o retry em workflow.py não tenha conseguido limpar (strip > tofu).
_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')


def _strip_ctrl(value):
    if isinstance(value, str):
        return _CTRL_RE.sub('', value)
    if isinstance(value, list):
        return [_strip_ctrl(v) for v in value]
    if isinstance(value, dict):
        return {k: _strip_ctrl(v) for k, v in value.items()}
    return value


def _sanitize_crm(crm: dict) -> dict:
    """Normaliza o CRM gerado pela IA antes de salvar.

    - Coage qualquer `channel` fora do conjunto canônico para 'atividade' (pega tokens crus
      do knowledge base como 'sem_acoes'/'mover_para_prospeccao' e legados 'ligação'/'auto').
    - Tira rótulos como "Script Final:" do início do `message` (o campo é só o texto).
    """
    for funnel in crm.get('funnels', []):
        for stage in funnel.get('stages', []):
            for day in stage.get('cadence', []):
                for action in day.get('actions', []):
                    if action.get('channel') not in CANONICAL_CHANNELS:
                        action['channel'] = 'atividade'
                    msg = action.get('message')
                    if isinstance(msg, str):
                        action['message'] = _MSG_LABEL_RE.sub('', msg, count=1)
    return crm


def _build_template(material_id=None, knowledge_name=None):
    """Monta o dict de material modelo p/ o workflow seguir como template.

    - material_id  -> GeneratedMaterial concluído: {crm, closing, qualification} (por seção).
    - knowledge_name -> doc .md indexado no S3: {reference_text}.
    Qualquer falha (fonte sumiu, S3 fora) = None: geração segue sem modelo, não derruba.
    """
    from .models import GeneratedMaterial

    try:
        if material_id:
            src = GeneratedMaterial.objects.filter(
                id=material_id, status='complete'
            ).first()
            if src:
                return {
                    'crm': src.crm,
                    'closing': src.closing,
                    'qualification': src.qualification,
                }
        elif knowledge_name:
            from .knowledge_api import KNOWLEDGE_PREFIX, _valid_name, storage

            if _valid_name(knowledge_name):
                key = KNOWLEDGE_PREFIX + knowledge_name
                if storage.exists(key):
                    with storage.open(key) as f:
                        text = f.read().decode('utf-8', errors='replace')
                    return {'reference_text': text}
    except Exception:
        logging.getLogger(__name__).warning('template build failed', exc_info=True)
    return None


async def _run_cancellable(workflow, onboarding_data, template, cache_key):
    """Roda o workflow numa Task cancelável, com watchdog fazendo polling do
    cache a cada 1s. Cancelar mata a Task de verdade (corta chamadas HTTP em
    andamento via CancelledError), não só descarta o resultado no fim."""
    from asgiref.sync import sync_to_async
    from django.core.cache import cache
    from django.db import connection

    def _check_cancel():
        try:
            return cache.get(cache_key)
        finally:
            # sync_to_async roda isso numa thread própria; sem fechar, a conexão
            # do DatabaseCache fica pendurada nessa thread até CONN_MAX_AGE (60s).
            connection.close()

    main = asyncio.ensure_future(workflow.arun(onboarding_data, template=template))
    while not main.done():
        if await sync_to_async(_check_cancel)():
            main.cancel()
            try:
                await main
            except asyncio.CancelledError:
                pass
            raise GenerationCancelled()
        await asyncio.wait({main}, timeout=1)
    return main.result()


def generate_materials_task(
    onboarding_id: int, template_material_id=None, template_knowledge_name=None
):
    from django.core.cache import cache
    from .models import OnboardingForm, GeneratedMaterial
    from .agents.workflow import MaterialWorkflow, onboarding_to_dict

    onboarding = OnboardingForm.objects.get(id=onboarding_id)
    material = GeneratedMaterial.objects.get(onboarding=onboarding)
    material.status = 'running'
    material.save(update_fields=['status'])

    template = _build_template(template_material_id, template_knowledge_name)
    cache_key = cancel_cache_key(onboarding_id)
    # Sem limpeza aqui: a flag pode ter sido setada com o material ainda
    # 'pending' (cancelado antes do worker pegar a task). O finally abaixo
    # já limpa ao fim de cada execução, e a chave expira sozinha (timeout=600).

    try:
        workflow = MaterialWorkflow()
        result = asyncio.run(
            _run_cancellable(
                workflow, onboarding_to_dict(onboarding), template, cache_key
            )
        )
        material.crm = _strip_ctrl(_sanitize_crm(result.crm.model_dump()))
        material.closing = _strip_ctrl(result.closing.model_dump())
        material.qualification = _strip_ctrl(result.qualification.model_dump())
        material.quality_alerts = _strip_ctrl(result.quality_alerts)
        material.status = 'complete'
    except GenerationCancelled:
        material.status = 'cancelled'
    except Exception as e:
        material.status = 'failed'
        material.error = str(e)
    finally:
        cache.delete(cache_key)
    material.save()

