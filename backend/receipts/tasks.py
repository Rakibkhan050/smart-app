from celery import shared_task
from django.conf import settings
from .models import Receipt
from .utils import render_receipt_pdf
import boto3
import qrcode
import io
from django.core.mail import send_mail


@shared_task(bind=True)
def generate_receipt_for_payment(self, payment_id=None, amount=None, currency='SAR', locale='en'):
    # Minimal implementation: create receipt record and upload PDF to S3
    if not payment_id:
        raise ValueError('payment_id required')

    # create basic receipt record
    receipt = Receipt.objects.create(payment_id=payment_id, tenant_id='default', invoice_number=f'INV-{payment_id}', amount=amount or 0, currency=currency)

    # generate QR code (simple text containing invoice URL)
    qr = qrcode.make(f"invoice:{receipt.invoice_number}")
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    # upload QR to S3
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                      region_name=settings.AWS_S3_REGION_NAME)
    qr_key = f"receipts/qr_{receipt.invoice_number}.png"
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=qr_key, Body=buf, ContentType='image/png')
    qr_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{qr_key}"

    # render PDF
    pdf = render_receipt_pdf(receipt, locale=locale)

    # upload PDF
    pdf_key = f"receipts/{receipt.invoice_number}.pdf"
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=pdf_key, Body=pdf, ContentType='application/pdf')
    pdf_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{pdf_key}"

    # update receipt
    receipt.s3_url = pdf_url
    receipt.qr_code_url = qr_url
    receipt.save()

    # send email with download link (uses Django's email backend configured for SendGrid)
    try:
        send_mail(
            subject=f"Your receipt {receipt.invoice_number}",
            message=f"Download your receipt: {pdf_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass

    return {'receipt_id': receipt.id, 'pdf_url': pdf_url}
