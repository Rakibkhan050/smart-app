from django.template.loader import render_to_string
from django.conf import settings


def render_receipt_pdf(receipt, locale='en'):
    template = 'receipts/receipt_en.html' if locale == 'en' else 'receipts/receipt_ar.html'
    html = render_to_string(template, {'receipt': receipt})

    try:
        # Import WeasyPrint lazily to avoid hard dependency at import time
        from weasyprint import HTML
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        pdf = HTML(string=html, base_url=base_url).write_pdf()
        return pdf
    except Exception:
        # Fallback to HTML bytes when weasyprint or system deps aren't available
        return html.encode('utf-8')

