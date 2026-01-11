import pytest
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from inventory.models import Product
from crm.models import Customer
from payments.models import Payment
from pos.models import Order, OrderItem
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_cashier_can_create_and_pay_order():
    User = get_user_model()
    tenant = Tenant.objects.create(slug='t1', name='T1')
    cashier = User.objects.create_user('cashier', 'c@example.com', 'pass')
    cashier.tenant = tenant
    cashier.role = 'cashier'
    cashier.save()

    product = Product.objects.create(tenant=tenant, name='P', sell_price=10, quantity=5)
    customer = Customer.objects.create(tenant=tenant, first_name='C', last_name='User')

    order = Order.objects.create(tenant=tenant, customer=customer)
    OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=product.sell_price)
    order.recalc_totals()

    client = APIClient()
    client.force_authenticate(user=cashier)

    resp = client.post(f'/api/pos/orders/{order.id}/pay/')
    assert resp.status_code == 200
    data = resp.json()
    assert 'payment_id' in data


@pytest.mark.django_db
def test_cashier_cannot_list_payments_but_manager_can():
    User = get_user_model()
    tenant = Tenant.objects.create(slug='t2', name='T2')
    cashier = User.objects.create_user('cashier2', 'c2@example.com', 'pass')
    cashier.tenant = tenant
    cashier.role = 'cashier'
    cashier.save()

    manager = User.objects.create_user('mgr', 'm@example.com', 'pass')
    manager.tenant = tenant
    manager.role = 'manager'
    manager.save()

    Payment.objects.create(payment_id='p1', tenant=tenant, provider='visa_mastercard', status='completed', amount=10)

    c = APIClient()
    c.force_authenticate(user=cashier)
    resp = c.get('/api/payments/payments/')
    assert resp.status_code == 403

    c2 = APIClient()
    c2.force_authenticate(user=manager)
    resp2 = c2.get('/api/payments/payments/')
    assert resp2.status_code == 200