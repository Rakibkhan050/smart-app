import pytest
import boto3
from receipts.tasks import generate_receipt_for_payment
from receipts.models import Receipt


@pytest.mark.django_db
def test_generate_receipt_fallback_to_local(monkeypatch, settings, tmp_path):
    # Make boto3.client raise to force local fallback
    def raise_client(*args, **kwargs):
        raise Exception('S3 not available')

    monkeypatch.setattr('boto3.client', raise_client)

    # ensure MEDIA_ROOT exists and is temporary
    settings.MEDIA_ROOT = str(tmp_path)

    res = generate_receipt_for_payment(payment_id='pfallback', amount=12.34, currency='SAR')
    assert 'receipt_id' in res
    r = Receipt.objects.get(id=res['receipt_id'])
    assert r.s3_url.startswith('file://')
    assert r.qr_code_url.startswith('file://')
