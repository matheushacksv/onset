from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Indexa os .md da knowledge base no pgvector'

    def add_arguments(self, parser):
        parser.add_argument('--recreate', action='store_true')

    def handle(self, *args, **options):
        from onboarding.agents.workflow import build_knowledge
        build_knowledge(recreate=options['recreate'])
        self.stdout.write(self.style.SUCCESS('Knowledge base indexada.'))
