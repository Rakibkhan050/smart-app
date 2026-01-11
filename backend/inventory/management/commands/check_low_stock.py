from django.core.management.base import BaseCommand
from inventory.tasks import check_low_stock_and_notify


class Command(BaseCommand):
    help = 'Check for low stock products and notify tenant admins (wrapper around Celery task).'

    def handle(self, *args, **options):
        # Try to run task synchronously for dev convenience
        try:
            check_low_stock_and_notify()
            self.stdout.write(self.style.SUCCESS('Low stock check executed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Low stock check failed: {e}'))
