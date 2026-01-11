from django.core.management.base import BaseCommand
from payments.models import Receipt
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Generate sample invoice (receipt)'

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(slug='demo', defaults={'name': 'Demo Tenant'})
        r = Receipt.objects.create(payment_id='demo-pmt-1', tenant=tenant, invoice_no='INV-DEMO-1', amount=100, vat_amount=5)
        self.stdout.write(self.style.SUCCESS(f"Generated receipt {r.invoice_no}"))
