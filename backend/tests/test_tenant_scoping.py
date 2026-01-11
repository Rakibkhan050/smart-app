from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tenants.models import Tenant
from inventory.models import Product
from crm.models import Customer
from payments.models import Payment
from delivery.models import Delivery
from inventory.admin import ProductAdmin
from crm.admin import CustomerAdmin
from payments.admin import PaymentAdmin, ReceiptAdmin
from delivery.admin import DeliveryAdmin


class TenantScopingTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Tenants (use `slug` field)
        self.tenant_a = Tenant.objects.create(slug='tenant-a', name='Tenant A')
        self.tenant_b = Tenant.objects.create(slug='tenant-b', name='Tenant B')

        # Users
        self.superuser = User.objects.create_superuser('root', 'root@example.com', 'rootpass')
        self.user_a = User.objects.create_user('alice', 'alice@example.com', 'pass')
        self.user_a.tenant = self.tenant_a
        self.user_a.save()

        self.client = APIClient()
        self.factory = RequestFactory()

        # Create objects across tenants
        Product.objects.create(tenant=self.tenant_a, name='AProd', sku='A1', sell_price=10)
        Product.objects.create(tenant=self.tenant_b, name='BProd', sku='B1', sell_price=20)

        Customer.objects.create(tenant=self.tenant_a, first_name='Ali', last_name='A')
        Customer.objects.create(tenant=self.tenant_b, first_name='Bob', last_name='B')

        Payment.objects.create(payment_id='pmt-a-1', tenant=self.tenant_a, provider='visa_mastercard', status='completed', amount=100)
        Payment.objects.create(payment_id='pmt-b-1', tenant=self.tenant_b, provider='visa_mastercard', status='completed', amount=200)

        Delivery.objects.create(tenant=self.tenant_a, order_reference='ORD-A-1', status='pending')
        Delivery.objects.create(tenant=self.tenant_b, order_reference='ORD-B-1', status='pending')

    def _extract_results(self, resp):
        data = resp.json()
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_admin_queryset_respects_tenant_for_product(self):
        admin_obj = ProductAdmin(Product, admin.site)
        request = self.factory.get('/admin/')
        request.user = self.user_a
        qs = admin_obj.get_queryset(request)
        names = list(qs.values_list('name', flat=True))
        self.assertIn('AProd', names)
        self.assertNotIn('BProd', names)

    def test_api_shows_only_tenant_products(self):
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/inventory/products/')
        self.assertEqual(resp.status_code, 200)
        items = self._extract_results(resp)
        names = [o['name'] for o in items]
        self.assertIn('AProd', names)
        self.assertNotIn('BProd', names)

    def test_api_create_assigns_tenant_product(self):
        self.client.force_authenticate(self.user_a)
        resp = self.client.post('/api/inventory/products/', {'name': 'NewP', 'sell_price': '5.00', 'cost_price': '1.00'})
        self.assertEqual(resp.status_code, 201)
        obj = Product.objects.get(id=resp.json()['id'])
        self.assertEqual(obj.tenant, self.tenant_a)

    def test_customer_api_tenant_scoping(self):
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/crm/customers/')
        self.assertEqual(resp.status_code, 200)
        items = self._extract_results(resp)
        names = [f"{o['first_name']}" for o in items]
        self.assertIn('Ali', names)
        self.assertNotIn('Bob', names)

    def test_payment_api_tenant_scoping(self):
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/payments/payments/')
        self.assertEqual(resp.status_code, 200)
        items = self._extract_results(resp)
        ids = [o['payment_id'] for o in items]
        self.assertIn('pmt-a-1', ids)
        self.assertNotIn('pmt-b-1', ids)

    def test_delivery_api_tenant_scoping(self):
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/delivery/deliveries/')
        self.assertEqual(resp.status_code, 200)
        items = self._extract_results(resp)
        refs = [o['order_reference'] for o in items]
        self.assertIn('ORD-A-1', refs)
        self.assertNotIn('ORD-B-1', refs)

    def test_superuser_sees_all(self):
        self.client.force_authenticate(self.superuser)
        resp = self.client.get('/api/inventory/products/')
        self.assertEqual(resp.status_code, 200)
        items = self._extract_results(resp)
        names = [o['name'] for o in items]
        self.assertIn('AProd', names)
        self.assertIn('BProd', names)
