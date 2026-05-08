import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Baixa MDs do MinIO e indexa no PgVector. Idempotente. Rodar 1x no deploy.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Drop e recreate da tabela vector antes de inserir',
        )

    def handle(self, *args, **opts):
        from onboarding.agents.workflow import build_knowledge

        recreate = opts['recreate']
        self.stdout.write(f'Building knowledge (recreate={recreate})...')
        t0 = time.time()
        build_knowledge(recreate=recreate)
        self.stdout.write(self.style.SUCCESS(f'Knowledge built in {time.time()-t0:.1f}s'))
