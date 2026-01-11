"""Tests for delivery workflows, assignment, status transitions, and RBAC."""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from delivery.models import Delivery, DeliveryPersonnel, Address, ShippingFeeRule

User = get_user_model()


class DeliveryModelTest(TestCase):
    """Test Delivery model methods."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.delivery = Delivery.objects.create(
            tenant=self.tenant,
            order_reference='ORD-001',
            tracking_number='TRK-001',
            status='pending'
        )
        self.personnel = DeliveryPersonnel.objects.create(
            tenant=self.tenant,
            name='John',
            phone='1234567890'
        )

    def test_assign_delivery_person(self):
        """Test assigning a delivery person."""
        self.delivery.assign(self.personnel)
        self.assertEqual(self.delivery.status, 'assigned')
        self.assertEqual(self.delivery.delivery_person, self.personnel)

    def test_delivery_status_transitions(self):
        """Test delivery status transitions."""
        self.assertEqual(self.delivery.status, 'pending')
        
        self.delivery.mark_picked_up()
        self.assertEqual(self.delivery.status, 'picked_up')
        
        self.delivery.mark_in_transit()
        self.assertEqual(self.delivery.status, 'in_transit')
        
        self.delivery.mark_delivered()
        self.assertEqual(self.delivery.status, 'delivered')

    def test_delivery_mark_failed(self):
        """Test marking delivery as failed."""
        self.delivery.mark_in_transit()
        self.delivery.mark_failed()
        self.assertEqual(self.delivery.status, 'failed')


class ShippingFeeRuleTest(TestCase):
    """Test shipping fee rule calculations."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.rule = ShippingFeeRule.objects.create(
            tenant=self.tenant,
            zone='Downtown',
            base_fee=50,
            per_km_fee=10,
            min_distance=0,
            max_distance=100
        )

    def test_calculate_fee(self):
        """Test fee calculation."""
        # 10 km => 50 + (10 * 10) = 150
        fee = self.rule.calculate_fee(10)
        self.assertEqual(fee, 150)
        
        # 5 km => 50 + (5 * 10) = 100
        fee = self.rule.calculate_fee(5)
        self.assertEqual(fee, 100)

    def test_fee_out_of_range(self):
        """Test fee calculation outside distance range."""
        # 150 km exceeds max_distance (100)
        fee = self.rule.calculate_fee(150)
        self.assertIsNone(fee)


class DeliveryAPITest(TestCase):
    """Test Delivery API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user('manager', 'mgr@test.com', 'pass')
        self.manager.tenant = self.tenant
        self.manager.role = 'manager'
        self.manager.save()
        
        self.cashier = User.objects.create_user('cashier', 'cash@test.com', 'pass')
        self.cashier.tenant = self.tenant
        self.cashier.role = 'cashier'
        self.cashier.save()
        
        self.client = APIClient()
        
        self.delivery = Delivery.objects.create(
            tenant=self.tenant,
            order_reference='ORD-001',
            tracking_number='TRK-001',
            status='pending'
        )
        
        self.personnel = DeliveryPersonnel.objects.create(
            tenant=self.tenant,
            name='John',
            phone='1234567890'
        )
        
        self.address = Address.objects.create(
            tenant=self.tenant,
            label='Home',
            line1='123 Main St',
            city='Riyadh',
            zone='Downtown'
        )

    def test_list_deliveries_as_manager(self):
        """Test manager can list deliveries."""
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/delivery/deliveries/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['tracking_number'], 'TRK-001')

    def test_list_deliveries_as_cashier(self):
        """Test cashier can list deliveries."""
        self.client.force_authenticate(self.cashier)
        resp = self.client.get('/api/delivery/deliveries/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)

    def test_create_delivery_as_manager(self):
        """Test manager can create delivery."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/delivery/deliveries/', {
            'order_reference': 'ORD-002',
            'tracking_number': 'TRK-002',
            'status': 'pending'
        })
        self.assertEqual(resp.status_code, 201)
        delivery = Delivery.objects.get(tracking_number='TRK-002')
        self.assertEqual(delivery.tenant, self.tenant)

    def test_assign_delivery_person(self):
        """Test assigning a delivery person via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(
            f'/api/delivery/deliveries/{self.delivery.id}/assign/',
            {'delivery_person_id': self.personnel.id}
        )
        self.assertEqual(resp.status_code, 200)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.delivery_person, self.personnel)
        self.assertEqual(self.delivery.status, 'assigned')

    def test_mark_picked_up_via_api(self):
        """Test marking delivery as picked up via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/delivery/deliveries/{self.delivery.id}/mark_picked_up/')
        self.assertEqual(resp.status_code, 200)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'picked_up')

    def test_mark_in_transit_via_api(self):
        """Test marking delivery as in transit via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/delivery/deliveries/{self.delivery.id}/mark_in_transit/')
        self.assertEqual(resp.status_code, 200)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'in_transit')

    def test_mark_delivered_via_api(self):
        """Test marking delivery as delivered via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/delivery/deliveries/{self.delivery.id}/mark_delivered/')
        self.assertEqual(resp.status_code, 200)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'delivered')

    def test_tenant_isolation(self):
        """Test that users only see their tenant's deliveries."""
        tenant_b = Tenant.objects.create(slug='b', name='Tenant B')
        delivery_b = Delivery.objects.create(
            tenant=tenant_b,
            order_reference='ORD-B-001',
            tracking_number='TRK-B-001'
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/delivery/deliveries/')
        data = resp.json()
        
        # Should only see tenant_a's delivery
        tracking_numbers = [d['tracking_number'] for d in data['results']]
        self.assertIn('TRK-001', tracking_numbers)
        self.assertNotIn('TRK-B-001', tracking_numbers)


class DeliveryPersonnelAPITest(TestCase):
    """Test DeliveryPersonnel API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user('manager', 'mgr@test.com', 'pass')
        self.manager.tenant = self.tenant
        self.manager.role = 'manager'
        self.manager.save()
        
        self.client = APIClient()

    def test_create_personnel(self):
        """Test creating delivery personnel."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/delivery/personnel/', {
            'name': 'John Doe',
            'phone': '1234567890',
            'active': True
        })
        self.assertEqual(resp.status_code, 201)
        personnel = DeliveryPersonnel.objects.get(name='John Doe')
        self.assertEqual(personnel.tenant, self.tenant)

    def test_list_personnel(self):
        """Test listing personnel."""
        DeliveryPersonnel.objects.create(
            tenant=self.tenant,
            name='John',
            phone='123'
        )
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/delivery/personnel/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)


class AddressAPITest(TestCase):
    """Test Address API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.cashier = User.objects.create_user('cashier', 'cash@test.com', 'pass')
        self.cashier.tenant = self.tenant
        self.cashier.role = 'cashier'
        self.cashier.save()
        
        self.client = APIClient()

    def test_create_address_as_cashier(self):
        """Test cashier can create address."""
        self.client.force_authenticate(self.cashier)
        resp = self.client.post('/api/delivery/addresses/', {
            'label': 'Home',
            'line1': '123 Main St',
            'city': 'Riyadh',
            'zone': 'Downtown',
            'latitude': '24.7136',
            'longitude': '46.6753'
        })
        self.assertEqual(resp.status_code, 201)
        address = Address.objects.get(label='Home')
        self.assertEqual(address.tenant, self.tenant)

    def test_list_addresses(self):
        """Test listing addresses."""
        Address.objects.create(
            tenant=self.tenant,
            label='Home',
            line1='123 Main St',
            city='Riyadh'
        )
        self.client.force_authenticate(self.cashier)
        resp = self.client.get('/api/delivery/addresses/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)


class ShippingFeeRuleAPITest(TestCase):
    """Test ShippingFeeRule API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.admin = User.objects.create_user('admin', 'admin@test.com', 'pass')
        self.admin.tenant = self.tenant
        self.admin.role = 'admin'
        self.admin.save()
        
        self.manager = User.objects.create_user('manager', 'mgr@test.com', 'pass')
        self.manager.tenant = self.tenant
        self.manager.role = 'manager'
        self.manager.save()
        
        self.client = APIClient()

    def test_create_shipping_fee_rule_as_admin(self):
        """Test admin can create shipping fee rule."""
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/delivery/shipping-fees/', {
            'zone': 'Downtown',
            'base_fee': '50.00',
            'per_km_fee': '10.00',
            'min_distance': 0,
            'max_distance': 100
        })
        self.assertEqual(resp.status_code, 201)
        rule = ShippingFeeRule.objects.get(zone='Downtown')
        self.assertEqual(rule.tenant, self.tenant)

    def test_manager_cannot_create_shipping_fee_rule(self):
        """Test manager cannot create shipping fee rule."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/delivery/shipping-fees/', {
            'zone': 'Downtown',
            'base_fee': '50.00'
        })
        self.assertEqual(resp.status_code, 403)

    def test_list_shipping_fee_rules(self):
        """Test listing shipping fee rules."""
        ShippingFeeRule.objects.create(
            tenant=self.tenant,
            zone='Downtown',
            base_fee=50,
            per_km_fee=10
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/delivery/shipping-fees/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
