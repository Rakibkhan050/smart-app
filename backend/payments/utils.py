import hmac
import hashlib
import os
from typing import Tuple


def verify_paytabs_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    # Example: PayTabs uses HMAC SHA256 over the payload
    mac = hmac.new(secret.encode('utf-8'), msg=payload_bytes, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_tap_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    # TAP signature example (depends on provider); commonly HMAC SHA256
    mac = hmac.new(secret.encode('utf-8'), msg=payload_bytes, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_hyperpay_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    # HyperPay example: might use SHA512 HMAC; adapt as required by provider
    mac = hmac.new(secret.encode('utf-8'), msg=payload_bytes, digestmod=hashlib.sha512)
    expected = mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def get_provider_secret(provider: str) -> str:
    provider = provider.lower()
    if provider == 'paytabs':
        return os.getenv('PAYTABS_SECRET', '')
    if provider == 'tap':
        return os.getenv('TAP_SECRET', '')
    if provider == 'hyperpay':
        return os.getenv('HYPERPAY_SECRET', '')
    return ''


# PDF generation for receipts (WeasyPrint)
from django.conf import settings
from django.template.loader import render_to_string


def generate_pdf_for_receipt(receipt) -> str:
    """Render receipt HTML and write a PDF file to MEDIA_ROOT/receipts.

    Returns a URL (using MEDIA_URL if set) or file:// path to the generated PDF.
    Updates the Receipt.url field on success.
    """
    template = 'payments/receipt_ar.html' if str(receipt.locale).lower().startswith('ar') else 'payments/receipt_en.html'
    context = {
        'receipt': receipt,
    }
    html = render_to_string(template, context)

    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')

    # Attempt to generate PDF using WeasyPrint; if system deps are missing, fall back to saving HTML
    try:
        from weasyprint import HTML
        pdf = HTML(string=html, base_url=base_url).write_pdf()

        receipts_dir = None
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
            os.makedirs(receipts_dir, exist_ok=True)
            filename = f"{receipt.invoice_no}.pdf"
            path = os.path.join(receipts_dir, filename)
            with open(path, 'wb') as f:
                f.write(pdf)
            if hasattr(settings, 'MEDIA_URL') and settings.MEDIA_URL:
                url = settings.MEDIA_URL.rstrip('/') + f"/receipts/{filename}"
            else:
                url = 'file://' + path
        else:
            # Fallback: write to /tmp
            tmp_path = f"/tmp/{receipt.invoice_no}.pdf"
            with open(tmp_path, 'wb') as f:
                f.write(pdf)
            url = 'file://' + tmp_path

    except Exception:
        # WeasyPrint or its system deps are not available in this container; write HTML so it can be inspected.
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
            os.makedirs(receipts_dir, exist_ok=True)
            filename = f"{receipt.invoice_no}.html"
            path = os.path.join(receipts_dir, filename)
        else:
            path = f"/tmp/{receipt.invoice_no}.html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        url = 'file://' + path

    # persist URL on receipt
    try:
        receipt.url = url
        receipt.save(update_fields=['url'])
    except Exception:
        # don't fail the whole operation if save fails
        pass

    return url
