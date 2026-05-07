import asyncio

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

