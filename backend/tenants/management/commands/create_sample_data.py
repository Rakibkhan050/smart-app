from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from tenants.models import Tenant
from accounts.models import User
from inventory.models import Product
from pos.models import Order, OrderItem
from payments.models import Payment
from delivery.models import Delivery
from finance.models import Expense
from crm.models import Customer


class Command(BaseCommand):
    help = 'Create sample data for 3D dashboard demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating sample data...'))
        
        # Create tenant
        tenant, created = Tenant.objects.get_or_create(
            name="Demo Store",
            defaults={'slug': 'demo-store'}
        )
        self.stdout.write(f"✅ Tenant: {tenant.name}")
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@demo.com',
                password='admin123',
                tenant=tenant,
                role='owner'
            )
            self.stdout.write(f"✅ Admin created: admin / admin123")
        
        # Create products
        categories = ['Electronics', 'Grocery', 'Pharmacy', 'Clothing']
        for cat in categories:
            for i in range(5):
                Product.objects.get_or_create(
                    tenant=tenant,
                    sku=f"{cat[:3].upper()}{i+1:03d}",
                    defaults={
                        'name': f"{cat} Item {i+1}",
                        'category': cat,
                        'quantity': random.randint(10, 200),
                        'cost_price': Decimal(str(random.uniform(10, 100))),
                        'sell_price': Decimal(str(random.uniform(15, 150))),
                        'unit': 'pcs'
                    }
                )
        self.stdout.write(f"✅ Products created")
        
        # Create customers
        for i in range(10):
            Customer.objects.get_or_create(
                tenant=tenant,
                email=f"customer{i}@demo.com",
                defaults={
                    'first_name': f"Customer",
                    'last_name': f"#{i+1}",
                    'phone': f"+123456{i:04d}"
                }
            )
        
        # Create sample orders for last 30 days
        products = list(Product.objects.filter(tenant=tenant))
        customers = list(Customer.objects.filter(tenant=tenant))
        
        if products and customers:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            for day in range(30):
                date = start_date + timedelta(days=day)
                for _ in range(random.randint(2, 6)):
                    order = Order.objects.create(
                        tenant=tenant,
                        customer=random.choice(customers),
                        status='paid',
                        total=Decimal('0'),
                        created_at=date
                    )
                    
                    total = Decimal('0')
                    for _ in range(random.randint(1, 4)):
                        product = random.choice(products)
                        qty = random.randint(1, 5)
                        price = product.sell_price
                        
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            unit_price=price
                        )
                        total += price * qty
                    
                    order.total = total
                    order.subtotal = total
                    order.save()
                    
                    Payment.objects.create(
                        tenant=tenant,
                        provider=random.choice(['visa', 'mastercard', 'apple_pay', 'mada', 'cash']),
                        amount=total,
                        currency='USD',
                        status='completed',
                        payment_id=f"PAY-{order.id}",
                        created_at=date
                    )
            
            self.stdout.write(f"✅ Orders and payments created")
        
        # Create expenses
        expense_cats = ['Rent', 'Utilities', 'Salaries', 'Marketing']
        for day in range(0, 30, 5):
            expense_date = (start_date + timedelta(days=day)).date()
            for cat in random.sample(expense_cats, 2):
                Expense.objects.create(
                    tenant=tenant,
                    category=cat,
                    amount=Decimal(str(random.uniform(500, 3000))),
                    description=f"{cat} expense",
                    expense_date=expense_date
                )
        
        self.stdout.write(f"✅ Expenses created")
        
        self.stdout.write(self.style.SUCCESS('\n✨ Sample data created successfully!'))
        self.stdout.write(f"🌐 Dashboard API: http://localhost:8000/api/finance/dashboard/3d-metrics/")
