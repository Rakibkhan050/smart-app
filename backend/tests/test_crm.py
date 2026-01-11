"""
Comprehensive tests for CRM features including loyalty accrual and purchase history.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from decimal import Decimal
from tenants.models import Tenant
from accounts.models import User
from crm.models import Customer, LoyaltyPoint, LoyaltyTransaction, PurchaseHistory
from pos.models import Order
from inventory.models import Product


class CRMModelTest(TestCase):
    """Test CRM models and business logic."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

    def test_customer_get_or_create_loyalty(self):
        """Test customer can get or create loyalty points."""
        loyalty = self.customer.get_or_create_loyalty()
        self.assertIsNotNone(loyalty)
        self.assertEqual(loyalty.points, 0)
        
        # Getting again should return same record
        loyalty2 = self.customer.get_or_create_loyalty()
        self.assertEqual(loyalty.id, loyalty2.id)

    def test_loyalty_add_points(self):
        """Test adding loyalty points."""
        loyalty = self.customer.get_or_create_loyalty()
        transaction = loyalty.add_points(100, reason='Test purchase')
        
        self.assertIsNotNone(transaction)
        self.assertEqual(loyalty.points, 100)
        self.assertEqual(transaction.points, 100)
        self.assertEqual(transaction.transaction_type, 'earn')

    def test_loyalty_add_points_negative_fails(self):
        """Test adding negative points returns None."""
        loyalty = self.customer.get_or_create_loyalty()
        transaction = loyalty.add_points(-50)
        self.assertIsNone(transaction)
        self.assertEqual(loyalty.points, 0)

    def test_loyalty_redeem_points(self):
        """Test redeeming loyalty points."""
        loyalty = self.customer.get_or_create_loyalty()
        loyalty.add_points(200, reason='Initial')
        
        transaction = loyalty.redeem_points(50, reason='Discount applied')
        self.assertIsNotNone(transaction)
        self.assertEqual(loyalty.points, 150)
        self.assertEqual(transaction.points, -50)
        self.assertEqual(transaction.transaction_type, 'redeem')

    def test_loyalty_redeem_insufficient_points(self):
        """Test cannot redeem more points than available."""
        loyalty = self.customer.get_or_create_loyalty()
        loyalty.add_points(50)
        
        transaction = loyalty.redeem_points(100)
        self.assertIsNone(transaction)
        self.assertEqual(loyalty.points, 50)

    def test_purchase_history_create_from_order(self):
        """Test creating purchase history and accruing loyalty from order."""
        order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            total=Decimal('250.00'),
            status='paid'
        )
        
        purchase = PurchaseHistory.create_from_order(order)
        
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.customer, self.customer)
        self.assertEqual(purchase.order, order)
        self.assertEqual(purchase.amount, Decimal('250.00'))
        self.assertEqual(purchase.loyalty_earned, 250)  # 1 point per currency unit
        
        # Verify loyalty points were added
        loyalty = self.customer.loyalty
        self.assertEqual(loyalty.points, 250)
        
        # Verify transaction was created
        transactions = LoyaltyTransaction.objects.filter(customer=self.customer)
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first().points, 250)

    def test_purchase_history_no_customer(self):
        """Test purchase history creation without customer returns None."""
        order = Order.objects.create(
            tenant=self.tenant,
            customer=None,
            total=Decimal('100.00')
        )
        
        purchase = PurchaseHistory.create_from_order(order)
        self.assertIsNone(purchase)


class CustomerAPITest(TestCase):
    """Test Customer API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='pass123',
            tenant=self.tenant,
            role='owner'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            email='cashier@test.com',
            password='pass123',
            tenant=self.tenant,
            role='cashier'
        )
        self.client = APIClient()
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )

    def test_list_customers(self):
        """Test listing customers."""
        self.client.force_authenticate(self.cashier)
        resp = self.client.get('/api/crm/customers/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['first_name'], 'Jane')

    def test_create_customer(self):
        """Test creating a customer."""
        self.client.force_authenticate(self.cashier)
        resp = self.client.post('/api/crm/customers/', {
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob@example.com',
            'phone': '555-1234'
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['first_name'], 'Bob')
        self.assertEqual(data['loyalty_points'], 0)

    def test_customer_purchase_history(self):
        """Test retrieving customer purchase history."""
        order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            total=Decimal('100.00'),
            status='paid'
        )
        PurchaseHistory.create_from_order(order)
        
        self.client.force_authenticate(self.owner)
        resp = self.client.get(f'/api/crm/customers/{self.customer.id}/purchase_history/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['amount'], '100.00')

    def test_customer_loyalty_transactions(self):
        """Test retrieving customer loyalty transactions."""
        loyalty = self.customer.get_or_create_loyalty()
        loyalty.add_points(50, reason='Welcome bonus')
        loyalty.redeem_points(20, reason='Discount')
        
        self.client.force_authenticate(self.owner)
        resp = self.client.get(f'/api/crm/customers/{self.customer.id}/loyalty_transactions/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)


class LoyaltyPointAPITest(TestCase):
    """Test Loyalty Points API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            tenant=self.tenant,
            role='manager'
        )
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='Alice',
            last_name='Wonder',
            email='alice@example.com'
        )
        self.loyalty = self.customer.get_or_create_loyalty()
        self.loyalty.add_points(200, reason='Initial')
        self.client = APIClient()

    def test_list_loyalty_points(self):
        """Test listing loyalty points."""
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/crm/loyalty/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['points'], 200)

    def test_redeem_points(self):
        """Test redeeming loyalty points via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/crm/loyalty/{self.loyalty.id}/redeem/', {
            'points': 50,
            'reason': 'Purchase discount'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['remaining_points'], 150)

    def test_redeem_insufficient_points(self):
        """Test redeeming more points than available fails."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/crm/loyalty/{self.loyalty.id}/redeem/', {
            'points': 300
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn('Insufficient', data['error'])

    def test_add_points_manual(self):
        """Test manually adding loyalty points via API."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/crm/loyalty/{self.loyalty.id}/add_points/', {
            'points': 75,
            'reason': 'Compensation'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_points'], 275)

    def test_add_negative_points_fails(self):
        """Test adding negative points fails."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/crm/loyalty/{self.loyalty.id}/add_points/', {
            'points': -10
        })
        self.assertEqual(resp.status_code, 400)


class PurchaseHistoryAPITest(TestCase):
    """Test Purchase History API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            tenant=self.tenant,
            role='manager'
        )
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='Charlie',
            last_name='Brown',
            email='charlie@example.com'
        )
        self.order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            total=Decimal('150.00'),
            status='paid'
        )
        PurchaseHistory.create_from_order(self.order)
        self.client = APIClient()

    def test_list_purchase_history(self):
        """Test listing purchase history."""
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/crm/purchase-history/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['amount'], '150.00')
        self.assertEqual(data['results'][0]['loyalty_earned'], 150)


class TenantIsolationTest(TestCase):
    """Test tenant isolation for CRM data."""

    def setUp(self):
        self.tenant_a = Tenant.objects.create(slug='a', name='Tenant A')
        self.tenant_b = Tenant.objects.create(slug='b', name='Tenant B')
        
        self.user_a = User.objects.create_user(
            username='user_a',
            email='a@test.com',
            password='pass123',
            tenant=self.tenant_a,
            role='manager'
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            email='b@test.com',
            password='pass123',
            tenant=self.tenant_b,
            role='manager'
        )
        
        self.customer_a = Customer.objects.create(
            tenant=self.tenant_a,
            first_name='A',
            email='customer_a@test.com'
        )
        self.customer_b = Customer.objects.create(
            tenant=self.tenant_b,
            first_name='B',
            email='customer_b@test.com'
        )
        
        self.client = APIClient()

    def test_customer_tenant_isolation(self):
        """Test users only see their tenant's customers."""
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/crm/customers/')
        data = resp.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['email'], 'customer_a@test.com')

    def test_purchase_history_tenant_isolation(self):
        """Test purchase history respects tenant boundaries."""
        order_a = Order.objects.create(
            tenant=self.tenant_a,
            customer=self.customer_a,
            total=Decimal('100.00')
        )
        order_b = Order.objects.create(
            tenant=self.tenant_b,
            customer=self.customer_b,
            total=Decimal('200.00')
        )
        
        PurchaseHistory.create_from_order(order_a)
        PurchaseHistory.create_from_order(order_b)
        
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/crm/purchase-history/')
        data = resp.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['amount'], '100.00')
