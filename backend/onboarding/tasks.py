import asyncio


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
        material.crm = result.crm.model_dump()
        material.closing = result.closing.model_dump()
        material.qualification = result.qualification.model_dump()
        material.quality_alerts = result.quality_alerts
        material.status = 'complete'
    except Exception as e:
        material.status = 'failed'
        material.error = str(e)
    material.save()

