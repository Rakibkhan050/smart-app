import pytest
from .adapters import get_adapter, SandboxAdapter


def test_get_sandbox_adapter_default():
    a = get_adapter('sandbox')
    assert isinstance(a, SandboxAdapter)


def test_create_payment_intent_sandbox():
    a = get_adapter('sandbox')
    intent = a.create_payment_intent(amount=100, currency='SAR')
    assert 'id' in intent and 'client_secret' in intent and intent['amount'] == 100


def test_verify_webhook_sandbox():
    a = get_adapter('sandbox')
    assert a.verify_webhook(payload={}, headers={'X-SANDBOX-SIGN': 'ok'})
    assert not a.verify_webhook(payload={}, headers={'X-SANDBOX-SIGN': 'bad'})
