import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tenants.models import Tenant
from inventory.models import Product
from crm.models import Customer
from pos.models import Order, OrderItem
from receipts import tasks as receipts_tasks
from receipts.models import Receipt


@pytest.mark.django_db
def test_order_pay_creates_payment_and_reduces_stock(monkeypatch):
    User = get_user_model()
    tenant = Tenant.objects.create(slug='pos-tenant', name='POS Tenant')
    user = User.objects.create_user('cashier', 'cashier@example.com', 'pass')
    user.tenant = tenant
    user.save()

    product = Product.objects.create(tenant=tenant, name='TProd', sell_price=50, quantity=10)
    customer = Customer.objects.create(tenant=tenant, first_name='Cust', last_name='One')

    order = Order.objects.create(tenant=tenant, customer=customer)
    OrderItem.objects.create(order=order, product=product, quantity=2, unit_price=product.sell_price)
    order.recalc_totals()

    client = APIClient()
    client.force_authenticate(user)

    called = {}

    def fake_delay(**kwargs):
        called.update(kwargs)
        return True

    monkeypatch.setattr('receipts.tasks.generate_receipt_for_payment.delay', fake_delay)

    resp = client.post(f'/api/pos/orders/{order.id}/pay/')
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert 'payment_id' in data

    order.refresh_from_db()
    product.refresh_from_db()
    assert order.status == 'paid'
    assert float(product.quantity) == 8.0
    assert called.get('payment_id') == data['payment_id']


@pytest.mark.django_db
def test_order_pay_fallback_sync_receipt(monkeypatch, tmp_path):
    # Simulate delay throwing and that sync fallback runs create a Receipt
    User = get_user_model()
    tenant = Tenant.objects.create(slug='pos-tenant-2', name='POS Tenant 2')
    user = User.objects.create_user('cashier2', 'cashier2@example.com', 'pass')
    user.tenant = tenant
    user.save()

    product = Product.objects.create(tenant=tenant, name='TProd2', sell_price=25, quantity=5)
    customer = Customer.objects.create(tenant=tenant, first_name='Cust', last_name='Two')

    order = Order.objects.create(tenant=tenant, customer=customer)
    OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=product.sell_price)
    order.recalc_totals()

    # make the async delay raise so code falls back to sync call
    def fake_delay_raise(*args, **kwargs):
        raise Exception('broker down')

    monkeypatch.setattr('receipts.tasks.generate_receipt_for_payment.delay', fake_delay_raise)

    client = APIClient()
    client.force_authenticate(user)

    resp = client.post(f'/api/pos/orders/{order.id}/pay/')
    assert resp.status_code in (200, 201)
    data = resp.json()

    # The sync fallback should create a Receipt record
    receipts = Receipt.objects.filter(payment_id=data['payment_id'])
    assert receipts.exists()
    r = receipts.first()
    assert r.s3_url is not None
    assert r.qr_code_url is not None