import pytest
from payments.utils import verify_paytabs_signature, get_provider_secret
import hmac, hashlib

@pytest.mark.parametrize('payload,secret', [ (b'{}', 'secret123'), (b'foo', 'abc') ])
def test_verify_paytabs_signature(payload, secret):
    import hmac
    mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
    sig = mac.hexdigest()
    assert verify_paytabs_signature(payload, sig, secret) is True
    assert verify_paytabs_signature(payload, 'bad', secret) is False
