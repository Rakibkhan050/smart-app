import pytest
from receipts.tasks import generate_receipt_for_payment
from receipts.models import Receipt


class DummyS3:
    def __init__(self):
        self.storage = {}

    def put_object(self, Bucket, Key, Body, ContentType=None):
        self.storage[Key] = {'body': Body, 'ContentType': ContentType}
        return True

    def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):
        return f"https://s3.example.com/{Params['Key']}?exp={ExpiresIn}"


@pytest.mark.django_db
def test_generate_receipt_uploads_to_s3_and_sends_email(monkeypatch, settings):
    dummy = DummyS3()
    monkeypatch.setattr('boto3.client', lambda *args, **kwargs: dummy)

    sent = {'sent': False}

    class DummySG:
        def __init__(self, api_key):
            pass
        def send(self, message):
            sent['sent'] = True
            return True

    monkeypatch.setattr('sendgrid.SendGridAPIClient', DummySG)

    settings.AWS_STORAGE_BUCKET_NAME = 'test-bucket'
    settings.AWS_S3_ENDPOINT_URL = 'https://s3.example.com'
    settings.SENDGRID_API_KEY = 'fake'

    res = generate_receipt_for_payment(payment_id='p_s3_1', amount=50, currency='SAR')
    assert 'receipt_id' in res
    r = Receipt.objects.get(id=res['receipt_id'])
    assert r.s3_key is not None
    assert r.get_presigned_url() is not None
    assert sent['sent'] is True