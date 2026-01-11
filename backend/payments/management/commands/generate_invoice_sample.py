from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'DISABLED: Sample invoice generation removed for production'

    def handle(self, *args, **options):
        self.stdout.write(self.style.ERROR('❌ Sample invoice generation is disabled in production.'))
        self.stdout.write('Receipts are automatically generated from real payments.')
        return
