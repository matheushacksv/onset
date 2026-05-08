from django.db import migrations

FUNIL_LABELS = {
    'trafego': 'Tráfego Pago',
    'prospeccao': 'Prospecção Ativa',
    'social': 'Social Selling',
    'carteira': 'Carteira / Reativação',
    'posvenda': 'Pós-venda / Indicação',
    'custom': 'Funil Customizado',
    'default': 'Pipeline'
}

def stages_to_funnels(apps, schema_editor):
    GeneratedMaterial = apps.get_model('onboarding', 'GeneratedMaterial')
    for m in GeneratedMaterial.objects.all():
        crm = m.crm or {}
        if 'funnels' in crm:
            continue
        stages = crm.get('stages', [])
        funis = list(m.onboarding.funis or []) if m.onboarding_id else []
        key = funis[0] if funis else 'default'
        m.crm = {
            'funnels': [{
                'key': key,
                'name': FUNIL_LABELS.get(key, 'Pipeline'),
                'stages': stages,
            }] if stages else []
        }
        m.save(update_fields=['crm'])

def funnels_to_stages(apps, schema_editor):
    GeneratedMaterial = apps.get_model('onboarding', 'GeneratedMaterial')
    for m in GeneratedMaterial.objects.all():
        crm = m.crm or {}
        funnels = crm.get('funnels', [])
        m.crm = {'stages': funnels[0]['stages'] if funnels else []}
        m.save(update_fields=['crm'])

class Migration(migrations.Migration):
    dependencies = [
        ('onboarding', '0005_alter_onboardingform_modelo_venda_and_more'),
    ]
    operations = [
        migrations.RunPython(stages_to_funnels, funnels_to_stages)
    ]
