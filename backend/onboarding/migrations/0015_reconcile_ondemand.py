from django.db import migrations


SCHEDULE_NAME = 'reconcile_recordings'
SCHEDULE_FUNC = 'onboarding.tasks.reconcile_recordings'


def to_ondemand(apps, schema_editor):
    """Remove o Schedule perpétuo (tipo MINUTES) criado na 0012. O reconcile passa
    a ser on-demand (django-q ONCE, armado pelo webhook). Para não orfanar jobs já
    pendentes no momento do deploy, arma uma rodada única imediata se houver fila.
    """
    from django.utils import timezone

    Schedule = apps.get_model('django_q', 'Schedule')
    RecordingJob = apps.get_model('onboarding', 'RecordingJob')

    # Só o perpétuo (schedule_type 'I'); nunca toca num ONCE ('O') em voo.
    Schedule.objects.filter(name=SCHEDULE_NAME, schedule_type='I').delete()

    if RecordingJob.objects.filter(status='pending').exists():
        Schedule.objects.update_or_create(
            name=SCHEDULE_NAME,
            defaults={
                'func': SCHEDULE_FUNC,
                'schedule_type': 'O',  # Schedule.ONCE
                'next_run': timezone.now(),
                'repeats': -1,  # ONCE + repeats<0 → django-q deleta após disparar
            },
        )


def to_perpetual(apps, schema_editor):
    """Reverso: recria o Schedule perpétuo da 0012."""
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.filter(name=SCHEDULE_NAME, schedule_type='O').delete()
    Schedule.objects.get_or_create(
        name=SCHEDULE_NAME,
        defaults={
            'func': SCHEDULE_FUNC,
            'schedule_type': 'I',  # Schedule.MINUTES
            'minutes': 5,
            'repeats': -1,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0014_pesquisa_outro_fields'),
        ('django_q', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(to_ondemand, to_perpetual),
    ]
