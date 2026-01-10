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
