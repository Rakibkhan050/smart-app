"""
Comprehensive tests for Celery automation tasks.
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from tenants.models import Tenant
from accounts.models import User
from inventory.models import Product
from delivery.models import Delivery, DeliveryPersonnel, Address
from pos.models import Order
from crm.models import Customer
from payments.models import Payment
from notifications.models import Notification


class LowStockTaskTest(TestCase):
    """Test low stock checking task."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            tenant=self.tenant,
            role='manager'
        )

    @patch('inventory.tasks.send_mail')
    def test_low_stock_notification(self, mock_send_mail):
        """Test low stock products trigger notifications."""
        from inventory.tasks import check_low_stock_and_notify
        
        # Create low stock product
        product = Product.objects.create(
            tenant=self.tenant,
            name='Test Product',
            sku='TEST-001',
            quantity=Decimal('5'),
            low_stock_threshold=Decimal('10'),
            unit='pcs'
        )
        
        result = check_low_stock_and_notify()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['low_stock_count'], 1)
        self.assertGreater(result['notifications_sent'], 0)
        
        # Check notification was created
        notifications = Notification.objects.filter(recipient=self.manager)
        self.assertEqual(notifications.count(), 1)
        self.assertIn('Low Stock Alert', notifications.first().title)

    def test_no_low_stock(self):
        """Test task returns success when no low stock."""
        from inventory.tasks import check_low_stock_and_notify
        
        # Create product with sufficient stock
        Product.objects.create(
            tenant=self.tenant,
            name='Well Stocked Product',
            sku='GOOD-001',
            quantity=Decimal('100'),
            low_stock_threshold=Decimal('10'),
            unit='pcs'
        )
        
        result = check_low_stock_and_notify()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['low_stock_count'], 0)

    def test_restock_product_task(self):
        """Test restocking product via task."""
        from inventory.tasks import restock_product
        
        product = Product.objects.create(
            tenant=self.tenant,
            name='Product',
            sku='PROD-001',
            quantity=Decimal('5'),
            low_stock_threshold=Decimal('10'),
            unit='pcs'
        )
        
        result = restock_product(product.id, 20, 'Purchase order received')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['added'], 20.0)
        
        product.refresh_from_db()
        self.assertEqual(product.quantity, Decimal('25'))


class ReceiptTaskTest(TestCase):
    """Test receipt generation and email tasks."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        self.payment = Payment.objects.create(
            tenant=self.tenant,
            payment_id='pay_test_123',
            provider='stripe',
            status='completed',
            amount=Decimal('100.00')
        )

    @patch('receipts.tasks.render_receipt_pdf')
    @patch('receipts.tasks.send_mail')
    def test_generate_receipt_for_payment(self, mock_send_mail, mock_render_pdf):
        """Test receipt generation task."""
        from receipts.tasks import generate_receipt_for_payment
        from receipts.models import Receipt
        
        mock_render_pdf.return_value = b'PDF_CONTENT'
        
        result = generate_receipt_for_payment(
            payment_id='pay_test_123',
            amount=100.00,
            currency='SAR'
        )
        
        self.assertIn('receipt_id', result)
        self.assertIn('pdf_url', result)
        
        # Check receipt was created
        receipt = Receipt.objects.get(id=result['receipt_id'])
        self.assertEqual(receipt.payment_id, 'pay_test_123')
        self.assertEqual(receipt.amount, Decimal('100.00'))

    @patch('receipts.tasks.generate_receipt_for_payment')
    @patch('receipts.tasks.send_mail')
    def test_auto_email_receipt_after_payment(self, mock_send_mail, mock_generate):
        """Test automatic receipt emailing after payment."""
        from receipts.tasks import auto_email_receipt_after_payment
        from receipts.models import Receipt
        
        # Create order linked to payment
        order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            payment=self.payment,
            status='paid',
            total=Decimal('100.00')
        )
        
        # Mock receipt generation
        receipt = Receipt.objects.create(
            payment_id='pay_test_123',
            tenant_id='test',
            invoice_number='INV-123',
            amount=Decimal('100.00'),
            currency='SAR',
            s3_url='http://example.com/receipt.pdf'
        )
        
        mock_generate.apply_async.return_value.get.return_value = {
            'receipt_id': receipt.id,
            'pdf_url': 'http://example.com/receipt.pdf'
        }
        
        result = auto_email_receipt_after_payment('pay_test_123')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['email_sent_to'], 'john@example.com')


class DeliveryTaskTest(TestCase):
    """Test delivery notification tasks."""

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
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com'
        )
        self.address = Address.objects.create(
            tenant=self.tenant,
            label='Home',
            line1='123 Main St',
            city='Riyadh'
        )
        self.delivery_person = DeliveryPersonnel.objects.create(
            tenant=self.tenant,
            name='Driver Bob',
            phone='555-1234'
        )
        self.order = Order.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status='paid',
            total=Decimal('100.00')
        )
        self.delivery = Delivery.objects.create(
            tenant=self.tenant,
            order_reference=f'ORD-{self.order.id}',
            address=self.address,
            tracking_number='TRK-001',
            status='pending',
            expected_delivery=timezone.now().date() + timedelta(days=2)
        )

    @patch('delivery.tasks.send_mail')
    def test_notify_delivery_status_change(self, mock_send_mail):
        """Test delivery status change notifications."""
        from delivery.tasks import notify_delivery_status_change
        
        result = notify_delivery_status_change(
            self.delivery.id,
            old_status='pending',
            new_status='assigned'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['new_status'], 'assigned')
        self.assertTrue(result['customer_notified'])
        
        # Check email was sent
        mock_send_mail.assert_called()
        call_args = mock_send_mail.call_args
        self.assertIn('jane@example.com', call_args[1]['recipient_list'])

    @patch('delivery.tasks.send_mail')
    def test_notify_failed_delivery(self, mock_send_mail):
        """Test notifications for failed deliveries."""
        from delivery.tasks import notify_delivery_status_change
        
        result = notify_delivery_status_change(
            self.delivery.id,
            old_status='in_transit',
            new_status='failed'
        )
        
        self.assertEqual(result['status'], 'success')
        
        # Check manager notification was created
        notifications = Notification.objects.filter(
            recipient=self.manager,
            title__icontains='failed'
        )
        self.assertGreater(notifications.count(), 0)

    @patch('delivery.tasks.send_mail')
    def test_check_overdue_deliveries(self, mock_send_mail):
        """Test checking for overdue deliveries."""
        from delivery.tasks import check_overdue_deliveries
        
        # Create overdue delivery
        overdue_delivery = Delivery.objects.create(
            tenant=self.tenant,
            order_reference=f'ORD-{self.order.id}-LATE',
            address=self.address,
            tracking_number='TRK-LATE',
            status='in_transit',
            expected_delivery=timezone.now().date() - timedelta(days=2)
        )
        
        result = check_overdue_deliveries()
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['overdue_count'], 0)
        self.assertGreater(result['notifications_sent'], 0)

    @patch('delivery.tasks.send_mail')
    def test_send_delivery_eta_update(self, mock_send_mail):
        """Test sending ETA updates."""
        from delivery.tasks import send_delivery_eta_update
        
        # Set delivery to in_transit
        self.delivery.status = 'in_transit'
        self.delivery.save()
        
        result = send_delivery_eta_update(self.delivery.id, estimated_minutes=45)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['estimated_minutes'], 45)
        self.assertTrue(result['customer_notified'])
        
        # Check email was sent
        mock_send_mail.assert_called()

    def test_eta_update_wrong_status(self):
        """Test ETA update is skipped for wrong status."""
        from delivery.tasks import send_delivery_eta_update
        
        # Delivery is in 'pending' status
        result = send_delivery_eta_update(self.delivery.id, estimated_minutes=30)
        
        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'not_in_transit')


class TaskRetryTest(TestCase):
    """Test task retry and error handling."""

    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test Tenant')

    @patch('inventory.tasks.Product.objects.filter')
    def test_low_stock_task_retry_on_failure(self, mock_filter):
        """Test low stock task retries on failure."""
        from inventory.tasks import check_low_stock_and_notify
        
        # Simulate database error
        mock_filter.side_effect = Exception('Database error')
        
        with self.assertRaises(Exception):
            check_low_stock_and_notify()

    def test_restock_nonexistent_product_fails(self):
        """Test restocking non-existent product raises error."""
        from inventory.tasks import restock_product
        
        with self.assertRaises(Exception):
            restock_product(99999, 10)


class CeleryBeatScheduleTest(TestCase):
    """Test Celery Beat schedule configuration."""

    def test_beat_schedule_exists(self):
        """Test that scheduled tasks are configured."""
        from django.conf import settings
        
        self.assertIn('CELERY_BEAT_SCHEDULE', dir(settings))
        schedule = settings.CELERY_BEAT_SCHEDULE
        
        # Check key scheduled tasks exist
        self.assertIn('check-low-stock-daily', schedule)
        self.assertIn('check-overdue-deliveries-daily', schedule)
        
        # Check task paths
        low_stock_task = schedule['check-low-stock-daily']
        self.assertEqual(low_stock_task['task'], 'inventory.tasks.check_low_stock_and_notify')
        
        overdue_task = schedule['check-overdue-deliveries-daily']
        self.assertEqual(overdue_task['task'], 'delivery.tasks.check_overdue_deliveries')
