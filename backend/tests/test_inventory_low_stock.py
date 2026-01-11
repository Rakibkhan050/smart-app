from django.test import TestCase
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from inventory.models import Product
from notifications.models import Notification
from inventory.tasks import check_low_stock_and_notify


class LowStockTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.tenant = Tenant.objects.create(slug='low-tenant', name='Low Tenant')
        # Create manager role user for tenant
        self.user = User.objects.create_user('mgr', 'mgr@example.com', 'pass')
        self.user.tenant = self.tenant
        self.user.is_staff = True
        self.user.role = 'manager'  # Set role to receive low stock notifications (lowercase)
        self.user.save()

    def test_low_stock_generates_notification(self):
        p = Product.objects.create(tenant=self.tenant, name='LowItem', sku='L1', quantity=1, low_stock_threshold=5, sell_price=10, cost_price=5)
        # Run task synchronously
        result = check_low_stock_and_notify()
        # Check notifications were created for manager
        notifs = Notification.objects.filter(
            recipient=self.user,
            title__icontains='Low Stock Alert'
        )
        self.assertTrue(notifs.exists())
        # Check the notification has the correct data structure
        notif = notifs.first()
        self.assertIn('product_ids', notif.data)
        self.assertIn(p.id, notif.data['product_ids'])
        # Check task result
        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['low_stock_count'], 0)
        self.assertGreater(result['notifications_sent'], 0)
