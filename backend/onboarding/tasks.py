import asyncio
import re

from .agents.schemas import CANONICAL_CHANNELS


def reconcile_recordings():
    """Processa RecordingJobs pendentes: acha a gravação no Drive do assessor e
    move pra pasta do cliente. Rodado periodicamente pelo Schedule do django-q.

    Idempotente e restart-safe: cada tentativa é curta (respeita timeout=60s do
    Q_CLUSTER). Gravação do Meet demora minutos a aparecer, então re-tenta a cada
    execução até achar ou estourar RECORDING_JOB_TIMEOUT_MIN.
    """
    import logging
    from datetime import timedelta
    from decouple import config
    from django.utils import timezone
    from .models import RecordingJob
    from . import google_services, pipedrive_services

    log = logging.getLogger(__name__)
    timeout_min = config('RECORDING_JOB_TIMEOUT_MIN', cast=int, default=120)
    deadline = timezone.now() - timedelta(minutes=timeout_min)

    for job in RecordingJob.objects.filter(status=RecordingJob.Status.PENDING):
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


def _notify(pipedrive_services, deal_id: int, content: str):
    try:
        pipedrive_services.create_note(deal_id, content)
    except Exception:
        pass


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


def generate_materials_task(onboarding_id: int):
    from .models import OnboardingForm, GeneratedMaterial
    from .agents.workflow import MaterialWorkflow, onboarding_to_dict

    onboarding = OnboardingForm.objects.get(id=onboarding_id)
    material = GeneratedMaterial.objects.get(onboarding=onboarding)
    material.status = 'running'
    material.save(update_fields=['status'])

    try:
        workflow = MaterialWorkflow()
        result = asyncio.run(workflow.arun(onboarding_to_dict(onboarding)))
        material.crm = _sanitize_crm(result.crm.model_dump())
        material.closing = result.closing.model_dump()
        material.qualification = result.qualification.model_dump()
        material.quality_alerts = result.quality_alerts
        material.status = 'complete'
    except Exception as e:
        material.status = 'failed'
        material.error = str(e)
    material.save()

