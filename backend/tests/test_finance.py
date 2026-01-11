"""
Comprehensive tests for Finance features including Expense, TaxRate, and P&L reports.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from tenants.models import Tenant
from accounts.models import User
from finance.models import Expense, TaxRate, ProfitLossReport
from pos.models import Order
from crm.models import Customer


class TaxRateModelTest(TestCase):
    """Test TaxRate model functionality."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.tax_rate = TaxRate.objects.create(
            tenant=self.tenant,
            name='VAT 15%',
            tax_type='vat',
            rate=Decimal('15.00')
        )

    def test_tax_rate_creation(self):
        """Test creating a tax rate."""
        self.assertEqual(self.tax_rate.name, 'VAT 15%')
        self.assertEqual(self.tax_rate.rate, Decimal('15.00'))

    def test_calculate_tax(self):
        """Test tax calculation."""
        base_amount = Decimal('100.00')
        tax = self.tax_rate.calculate_tax(base_amount)
        self.assertEqual(tax, Decimal('15.00'))


class ExpenseModelTest(TestCase):
    """Test Expense model functionality."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.tax_rate = TaxRate.objects.create(
            tenant=self.tenant,
            name='VAT 15%',
            tax_type='vat',
            rate=Decimal('15.00')
        )

    def test_expense_auto_calculate_tax(self):
        """Test expense automatically calculates tax."""
        expense = Expense.objects.create(
            tenant=self.tenant,
            category='supplies',
            description='Office supplies',
            amount=Decimal('200.00'),
            tax_rate=self.tax_rate,
            expense_date=date.today()
        )
        
        self.assertEqual(expense.tax_amount, Decimal('30.00'))
        self.assertEqual(expense.total_amount, Decimal('230.00'))

    def test_expense_without_tax(self):
        """Test expense without tax rate."""
        expense = Expense.objects.create(
            tenant=self.tenant,
            category='rent',
            description='Monthly rent',
            amount=Decimal('1000.00'),
            expense_date=date.today()
        )
        
        self.assertEqual(expense.tax_amount, Decimal('0.00'))
        self.assertEqual(expense.total_amount, Decimal('1000.00'))

    def test_mark_expense_paid(self):
        """Test marking expense as paid."""
        expense = Expense.objects.create(
            tenant=self.tenant,
            category='utilities',
            description='Electricity bill',
            amount=Decimal('150.00'),
            expense_date=date.today()
        )
        
        self.assertFalse(expense.paid)
        self.assertIsNone(expense.payment_date)
        
        expense.paid = True
        expense.payment_date = date.today()
        expense.save()
        
        self.assertTrue(expense.paid)
        self.assertIsNotNone(expense.payment_date)


class ProfitLossReportTest(TestCase):
    """Test P&L report generation."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='Test',
            last_name='Customer'
        )
        
        self.start_date = date(2026, 1, 1)
        self.end_date = date(2026, 1, 31)

    def test_generate_report_with_revenue(self):
        """Test P&L report generation with revenue."""
        # Create paid orders
        order1 = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status='paid',
            total=Decimal('500.00'),
            tax_amount=Decimal('50.00')
        )
        order1.created_at = timezone.datetime(2026, 1, 15, tzinfo=timezone.utc)
        order1.save()
        
        order2 = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status='paid',
            total=Decimal('300.00'),
            tax_amount=Decimal('30.00')
        )
        order2.created_at = timezone.datetime(2026, 1, 20, tzinfo=timezone.utc)
        order2.save()
        
        report = ProfitLossReport.generate_report(self.tenant, self.start_date, self.end_date)
        
        self.assertEqual(report.total_revenue, Decimal('800.00'))
        self.assertEqual(report.total_tax_collected, Decimal('80.00'))

    def test_generate_report_with_expenses(self):
        """Test P&L report generation with expenses."""
        # Create expenses
        Expense.objects.create(
            tenant=self.tenant,
            category='cogs',
            description='Product cost',
            amount=Decimal('200.00'),
            expense_date=date(2026, 1, 10)
        )
        
        Expense.objects.create(
            tenant=self.tenant,
            category='rent',
            description='Office rent',
            amount=Decimal('1000.00'),
            expense_date=date(2026, 1, 5)
        )
        
        report = ProfitLossReport.generate_report(self.tenant, self.start_date, self.end_date)
        
        self.assertEqual(report.cogs, Decimal('200.00'))
        self.assertEqual(report.operating_expenses, Decimal('1000.00'))

    def test_generate_complete_report(self):
        """Test complete P&L report with revenue and expenses."""
        # Create revenue
        order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status='paid',
            total=Decimal('1000.00'),
            tax_amount=Decimal('100.00')
        )
        order.created_at = timezone.datetime(2026, 1, 15, tzinfo=timezone.utc)
        order.save()
        
        # Create expenses
        Expense.objects.create(
            tenant=self.tenant,
            category='cogs',
            description='Cost of goods',
            amount=Decimal('400.00'),
            expense_date=date(2026, 1, 10)
        )
        
        Expense.objects.create(
            tenant=self.tenant,
            category='salaries',
            description='Staff wages',
            amount=Decimal('300.00'),
            expense_date=date(2026, 1, 25)
        )
        
        report = ProfitLossReport.generate_report(self.tenant, self.start_date, self.end_date)
        
        self.assertEqual(report.total_revenue, Decimal('1000.00'))
        self.assertEqual(report.cogs, Decimal('400.00'))
        self.assertEqual(report.operating_expenses, Decimal('300.00'))
        self.assertEqual(report.gross_profit, Decimal('600.00'))
        self.assertEqual(report.net_profit, Decimal('300.00'))


class TaxRateAPITest(TestCase):
    """Test TaxRate API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            tenant=self.tenant,
            role='manager'
        )
        self.client = APIClient()

    def test_list_tax_rates(self):
        """Test listing tax rates."""
        TaxRate.objects.create(
            tenant=self.tenant,
            name='VAT 15%',
            tax_type='vat',
            rate=Decimal('15.00')
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/tax-rates/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'VAT 15%')

    def test_create_tax_rate(self):
        """Test creating a tax rate."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/finance/tax-rates/', {
            'name': 'Sales Tax 5%',
            'tax_type': 'sales',
            'rate': '5.00',
            'is_active': True
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['name'], 'Sales Tax 5%')
        self.assertEqual(data['rate'], '5.00')


class ExpenseAPITest(TestCase):
    """Test Expense API endpoints."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            tenant=self.tenant,
            role='manager'
        )
        self.tax_rate = TaxRate.objects.create(
            tenant=self.tenant,
            name='VAT 15%',
            tax_type='vat',
            rate=Decimal('15.00')
        )
        self.client = APIClient()

    def test_list_expenses(self):
        """Test listing expenses."""
        Expense.objects.create(
            tenant=self.tenant,
            category='supplies',
            description='Office supplies',
            amount=Decimal('100.00'),
            expense_date=date.today()
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/expenses/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['results']), 1)

    def test_create_expense(self):
        """Test creating an expense."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/finance/expenses/', {
            'category': 'rent',
            'description': 'Monthly office rent',
            'amount': '2000.00',
            'expense_date': date.today().isoformat(),
            'paid': False
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['description'], 'Monthly office rent')
        self.assertEqual(data['amount'], '2000.00')

    def test_create_expense_with_tax(self):
        """Test creating expense with tax."""
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/finance/expenses/', {
            'category': 'supplies',
            'description': 'Equipment',
            'amount': '500.00',
            'tax_rate': self.tax_rate.id,
            'expense_date': date.today().isoformat()
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['tax_amount'], '75.00')
        self.assertEqual(data['total_amount'], '575.00')

    def test_expenses_by_category(self):
        """Test getting expenses grouped by category."""
        Expense.objects.create(
            tenant=self.tenant,
            category='rent',
            description='Rent',
            amount=Decimal('1000.00'),
            expense_date=date.today()
        )
        Expense.objects.create(
            tenant=self.tenant,
            category='rent',
            description='More rent',
            amount=Decimal('500.00'),
            expense_date=date.today()
        )
        Expense.objects.create(
            tenant=self.tenant,
            category='supplies',
            description='Supplies',
            amount=Decimal('200.00'),
            expense_date=date.today()
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/expenses/by_category/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(len(data), 2)
        rent_total = next(item for item in data if item['category'] == 'rent')
        self.assertEqual(rent_total['total'], Decimal('1500.00'))

    def test_mark_expense_paid(self):
        """Test marking expense as paid."""
        expense = Expense.objects.create(
            tenant=self.tenant,
            category='utilities',
            description='Electric bill',
            amount=Decimal('300.00'),
            expense_date=date.today()
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.post(f'/api/finance/expenses/{expense.id}/mark_paid/', {
            'payment_date': date.today().isoformat()
        })
        self.assertEqual(resp.status_code, 200)
        
        expense.refresh_from_db()
        self.assertTrue(expense.paid)


class ReportAPITest(TestCase):
    """Test financial report API endpoints."""

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
            first_name='Test',
            last_name='Customer'
        )
        self.client = APIClient()

    def test_profit_loss_report(self):
        """Test P&L report endpoint."""
        # Create test data
        order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status='paid',
            total=Decimal('1000.00'),
            tax_amount=Decimal('100.00')
        )
        
        Expense.objects.create(
            tenant=self.tenant,
            category='cogs',
            description='Cost',
            amount=Decimal('300.00'),
            expense_date=date.today()
        )
        
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/reports/profit_loss/', {
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat()
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn('total_revenue', data)
        self.assertIn('net_profit', data)

    def test_vat_aggregation_report(self):
        """Test VAT aggregation endpoint."""
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/reports/vat_aggregation/', {
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat()
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn('vat_on_sales', data)
        self.assertIn('vat_on_purchases', data)
        self.assertIn('net_vat_payable', data)

    def test_dashboard_metrics(self):
        """Test dashboard metrics endpoint."""
        self.client.force_authenticate(self.manager)
        resp = self.client.get('/api/finance/reports/dashboard/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn('total_revenue', data)
        self.assertIn('total_expenses', data)
        self.assertIn('net_profit', data)
        self.assertIn('profit_margin', data)
        self.assertIn('expense_by_category', data)


class TenantIsolationTest(TestCase):
    """Test tenant isolation for finance data."""

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
        
        self.client = APIClient()

    def test_expense_tenant_isolation(self):
        """Test users only see their tenant's expenses."""
        Expense.objects.create(
            tenant=self.tenant_a,
            category='rent',
            description='Tenant A rent',
            amount=Decimal('1000.00'),
            expense_date=date.today()
        )
        Expense.objects.create(
            tenant=self.tenant_b,
            category='rent',
            description='Tenant B rent',
            amount=Decimal('2000.00'),
            expense_date=date.today()
        )
        
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/finance/expenses/')
        data = resp.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['description'], 'Tenant A rent')

    def test_tax_rate_tenant_isolation(self):
        """Test tax rate tenant isolation."""
        TaxRate.objects.create(
            tenant=self.tenant_a,
            name='A VAT',
            tax_type='vat',
            rate=Decimal('15.00')
        )
        TaxRate.objects.create(
            tenant=self.tenant_b,
            name='B VAT',
            tax_type='vat',
            rate=Decimal('20.00')
        )
        
        self.client.force_authenticate(self.user_a)
        resp = self.client.get('/api/finance/tax-rates/')
        data = resp.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'A VAT')
