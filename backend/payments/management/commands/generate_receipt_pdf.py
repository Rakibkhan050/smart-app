from django.core.management.base import BaseCommand
from payments.models import Receipt
from payments.utils import generate_pdf_for_receipt

class Command(BaseCommand):
    help = 'Generate PDF for a receipt'

    def add_arguments(self, parser):
        parser.add_argument('invoice_no')

    def handle(self, *args, **options):
        inv = options['invoice_no']
        r = Receipt.objects.get(invoice_no=inv)
        url = generate_pdf_for_receipt(r)
        self.stdout.write(self.style.SUCCESS(f'Generated PDF at {url}'))
