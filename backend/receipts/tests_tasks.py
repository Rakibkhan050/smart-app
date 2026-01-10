import pytest
from django.contrib.auth import get_user_model
from receipts.tasks import generate_receipt_for_payment
from receipts.models import Receipt
from unittest import mock

@pytest.mark.django_db
def test_generate_receipt_for_payment_creates_receipt(monkeypatch):
    # Patch boto3 client to avoid real S3 calls
    class DummyS3:
        def put_object(self, Bucket, Key, Body, ContentType=None):
            return True
        def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):
            return f"https://s3.example.com/{Params['Key']}"

    monkeypatch.setattr('boto3.client', lambda *args, **kwargs: DummyS3())

    res = generate_receipt_for_payment(payment_id='pay_1', amount=100, currency='SAR')
    assert 'receipt_id' in res
    r = Receipt.objects.get(id=res['receipt_id'])
    assert r.s3_url is not None
    assert r.qr_code_url is not None
