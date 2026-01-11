from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from .models import Receipt
from .utils import render_receipt_pdf
import boto3
import qrcode
import io
import os
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 120},
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True
)
def generate_receipt_for_payment(self, payment_id=None, amount=None, currency='SAR', locale='en'):
    # Robust implementation: create receipt record, upload PDF and QR to S3 if available, else write to MEDIA and return file:// urls
    if not payment_id:
        raise ValueError('payment_id required')

    # attempt to resolve payment and tenant
    payment = None
    try:
        from payments.models import Payment
        payment = Payment.objects.filter(payment_id=payment_id).first()
    except Exception:
        payment = None

    tenant_id = 'default'
    if payment and getattr(payment, 'tenant', None):
        tenant = payment.tenant
        tenant_id = getattr(tenant, 'slug', str(getattr(tenant, 'id', 'default')))

    invoice_number = f'INV-{payment_id}'
    receipt = Receipt.objects.create(payment_id=payment_id, tenant_id=tenant_id, invoice_number=invoice_number, amount=amount or (getattr(payment, 'amount', 0)), currency=currency)

    # generate QR code (simple text containing invoice URL)
    qr = qrcode.make(f"invoice:{receipt.invoice_number}")
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    qr_url = None
    pdf_url = None

    # try upload to S3; if fails, write to local MEDIA_ROOT
    s3 = None
    try:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                          region_name=settings.AWS_S3_REGION_NAME)
    except Exception:
        s3 = None

    # QR
    if s3 and settings.AWS_STORAGE_BUCKET_NAME:
        try:
            qr_key = f"receipts/qr_{receipt.invoice_number}.png"
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=qr_key, Body=buf, ContentType='image/png')
            qr_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{qr_key}"
            receipt.qr_code_url = qr_url
            receipt.save(update_fields=['qr_code_url'])
            receipt_qr_key = qr_key
        except Exception:
            s3 = None
            receipt_qr_key = None

    if not qr_url:
        # write locally
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'receipts'), exist_ok=True)
        qr_path = os.path.join(settings.MEDIA_ROOT, 'receipts', f"qr_{receipt.invoice_number}.png")
        with open(qr_path, 'wb') as f:
            f.write(buf.getvalue())
        qr_url = f"file://{qr_path}"
        receipt.qr_code_url = qr_url
        receipt.save(update_fields=['qr_code_url'])
        receipt_qr_key = None

    # render PDF
    pdf = render_receipt_pdf(receipt, locale=locale)

    # upload PDF or write local
    receipt_pdf_key = None
    if s3 and settings.AWS_STORAGE_BUCKET_NAME:
        try:
            pdf_key = f"receipts/{receipt.invoice_number}.pdf"
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=pdf_key, Body=pdf, ContentType='application/pdf')
            receipt_pdf_key = pdf_key
            # generate presigned url
            try:
                pdf_url = s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': pdf_key}, ExpiresIn=3600)
            except Exception:
                pdf_url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{pdf_key}"
        except Exception:
            pdf_url = None

    if not pdf_url:
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'receipts'), exist_ok=True)
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'receipts', f"{receipt.invoice_number}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)
        pdf_url = f"file://{pdf_path}"

    # update receipt with s3 keys and url
    if receipt_pdf_key:
        receipt.s3_key = receipt_pdf_key
        receipt.s3_url = pdf_url
    else:
        receipt.s3_key = None
        receipt.s3_url = pdf_url

    if receipt_qr_key:
        # store QR as object key for reference if needed
        pass

    receipt.save()

    # send notification email (SendGrid preferred)
    try:
        if getattr(settings, 'SENDGRID_API_KEY', None):
            # use SendGrid API to send a message with link
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            sg = SendGridAPIClient(getattr(settings, 'SENDGRID_API_KEY'))
            link = receipt.get_presigned_url() or receipt.s3_url
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=[settings.DEFAULT_FROM_EMAIL],
                subject=f"Your receipt {receipt.invoice_number}",
                html_content=f"<p>Download your receipt: <a href=\"{link}\">{link}</a></p>")
            try:
                sg.send(message)
            except Exception:
                # fallback to send_mail
                send_mail(
                    subject=f"Your receipt {receipt.invoice_number}",
                    message=f"Download your receipt: {receipt.s3_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
        else:
            send_mail(
                subject=f"Your receipt {receipt.invoice_number}",
                message=f"Download your receipt: {receipt.s3_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
    except Exception:
        pass

    return {'receipt_id': receipt.id, 'pdf_url': pdf_url}


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 180},
    retry_backoff=True
)
def auto_email_receipt_after_payment(self, payment_id, customer_email=None):
    """
    Automatically email receipt to customer after payment is completed.
    This task is triggered when an order payment is confirmed.
    
    Args:
        payment_id: Payment ID to generate receipt for
        customer_email: Customer email address (optional)
    """
    try:
        from payments.models import Payment
        
        # Get payment details
        payment = Payment.objects.filter(payment_id=payment_id).first()
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return {'status': 'error', 'message': 'Payment not found'}
        
        if payment.status != 'completed':
            logger.warning(f"Payment {payment_id} status is {payment.status}, not completed")
            return {'status': 'skipped', 'message': 'Payment not completed'}
        
        # Get customer email from order if available
        if not customer_email:
            try:
                from pos.models import Order
                order = Order.objects.filter(payment=payment).select_related('customer').first()
                if order and order.customer and order.customer.email:
                    customer_email = order.customer.email
            except Exception as e:
                logger.warning(f"Could not find order/customer for payment {payment_id}: {e}")
        
        if not customer_email:
            logger.warning(f"No customer email for payment {payment_id}")
            return {'status': 'skipped', 'message': 'No customer email'}
        
        # Generate receipt (will create receipt record and PDF)
        result = generate_receipt_for_payment.apply_async(
            args=[payment_id],
            kwargs={
                'amount': float(payment.amount),
                'currency': getattr(payment, 'currency', 'SAR'),
                'locale': 'en'
            }
        ).get(timeout=30)
        
        receipt = Receipt.objects.get(id=result['receipt_id'])
        pdf_url = result['pdf_url']
        
        # Send email with PDF attachment or link
        subject = f"Receipt for your purchase - {receipt.invoice_number}"
        body = f"""
Thank you for your purchase!

Invoice Number: {receipt.invoice_number}
Amount: {receipt.amount} {receipt.currency}
Date: {receipt.created_at.strftime('%Y-%m-%d %H:%M')}

You can download your receipt here: {pdf_url}

Best regards,
Your Store Team
"""
        
        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[customer_email]
            )
            
            # Attach PDF if local file
            if pdf_url.startswith('file://'):
                pdf_path = pdf_url.replace('file://', '')
                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        email.attach(
                            f'{receipt.invoice_number}.pdf',
                            f.read(),
                            'application/pdf'
                        )
            
            email.send(fail_silently=False)
            
            logger.info(f"Receipt email sent to {customer_email} for payment {payment_id}")
            
            return {
                'status': 'success',
                'payment_id': payment_id,
                'receipt_id': receipt.id,
                'email_sent_to': customer_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send receipt email: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Auto-email receipt failed for payment {payment_id}: {e}")
        raise
