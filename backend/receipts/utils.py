from django.template.loader import render_to_string
from django.conf import settings
import weasyprint


def render_receipt_pdf(receipt, locale='en'):
    template = 'receipts/receipt_en.html' if locale == 'en' else 'receipts/receipt_ar.html'
    html = render_to_string(template, {'receipt': receipt})
    pdf = weasyprint.HTML(string=html).write_pdf()
    return pdf
