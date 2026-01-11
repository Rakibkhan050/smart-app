#!/usr/bin/env python
"""
Create sample tenant and data for 3D dashboard testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

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
from finance.models import Expense, ProfitLossReport
from crm.models import Customer

def create_sample_data():
    print("🚀 Creating sample data for 3D Dashboard...")
    
    # Create tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Demo Store",
        defaults={
            'is_active': True,
            'subscription_tier': 'premium'
        }
    )
    if created:
        print(f"✅ Created tenant: {tenant.name}")
    else:
        print(f"✅ Using existing tenant: {tenant.name}")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            'email': 'admin@demo.com',
            'role': 'owner',
            'tenant': tenant,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: admin / admin123")
    else:
        print(f"✅ Using existing admin user")
    
    # Create customers
    customers = []
    for i in range(10):
        customer, _ = Customer.objects.get_or_create(
            tenant=tenant,
            email=f"customer{i+1}@demo.com",
            defaults={
                'name': f"Customer {i+1}",
                'phone': f"+1234567{i:03d}",
                'loyalty_points': random.randint(0, 500)
            }
        )
        customers.append(customer)
    print(f"✅ Created {len(customers)} customers")
    
    # Create products
    categories = ['Electronics', 'Grocery', 'Pharmacy', 'Clothing']
    products = []
    for cat in categories:
        for i in range(5):
            product, _ = Product.objects.get_or_create(
                tenant=tenant,
                sku=f"{cat[:3].upper()}{i+1:03d}",
                defaults={
                    'name': f"{cat} Product {i+1}",
                    'category': cat,
                    'brand': f"Brand {chr(65+i)}",
                    'quantity': random.randint(10, 200),
                    'low_stock_threshold': 20,
                    'cost_price': Decimal(str(random.uniform(10, 100))),
                    'sell_price': Decimal(str(random.uniform(15, 150))),
                    'unit': 'pcs'
                }
            )
            products.append(product)
    print(f"✅ Created {len(products)} products")
    
    # Create orders and payments for last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    orders_created = 0
    payments_created = 0
    
    for day in range(30):
        date = start_date + timedelta(days=day)
        num_orders = random.randint(2, 8)
        
        for _ in range(num_orders):
            # Create order
            customer = random.choice(customers)
            order = Order.objects.create(
                tenant=tenant,
                customer=customer,
                status='completed',
                total_amount=Decimal('0'),
                created_at=date
            )
            
            # Add order items
            total = Decimal('0')
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                price = product.sell_price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=price,
                    subtotal=price * quantity
                )
                total += price * quantity
            
            order.total_amount = total
            order.save()
            orders_created += 1
            
            # Create payment
            payment_methods = ['visa', 'mastercard', 'apple_pay', 'cash', 'mada']
            Payment.objects.create(
                tenant=tenant,
                order=order,
                provider=random.choice(payment_methods),
                amount=total,
                currency='USD',
                status='completed',
                payment_id=f"PAY-{order.id}",
                created_at=date
            )
            payments_created += 1
    
    print(f"✅ Created {orders_created} orders")
    print(f"✅ Created {payments_created} payments")
    
    # Create expenses
    expense_categories = ['Rent', 'Utilities', 'Salaries', 'Marketing', 'Supplies']
    expenses_created = 0
    
    for day in range(0, 30, 3):
        date = start_date + timedelta(days=day)
        for cat in random.sample(expense_categories, 2):
            Expense.objects.create(
                tenant=tenant,
                category=cat,
                amount=Decimal(str(random.uniform(500, 5000))),
                description=f"{cat} expense",
                date=date.date()
            )
            expenses_created += 1
    
    print(f"✅ Created {expenses_created} expenses")
    
    # Create deliveries
    statuses = ['pending', 'assigned', 'picked_up', 'in_transit', 'delivered']
    cities = [
        ('New York', 40.7128, -74.0060),
        ('Los Angeles', 34.0522, -118.2437),
        ('Chicago', 41.8781, -87.6298),
        ('Houston', 29.7604, -95.3698),
        ('Phoenix', 33.4484, -112.0740)
    ]
    
    deliveries_created = 0
    for day in range(30):
        date = start_date + timedelta(days=day)
        for _ in range(random.randint(1, 4)):
            city, lat, lon = random.choice(cities)
            status = random.choice(statuses)
            
            Delivery.objects.create(
                tenant=tenant,
                order=random.choice(Order.objects.filter(tenant=tenant)[:20]),
                status=status,
                address=f"{random.randint(100, 999)} Main St, {city}",
                gps_latitude=Decimal(str(lat + random.uniform(-0.1, 0.1))),
                gps_longitude=Decimal(str(lon + random.uniform(-0.1, 0.1))),
                shipping_fee=Decimal(str(random.uniform(5, 25))),
                estimated_delivery=date + timedelta(hours=random.randint(2, 48)),
                created_at=date
            )
            deliveries_created += 1
    
    print(f"✅ Created {deliveries_created} deliveries")
    
    print("\n✨ Sample data creation complete!")
    print(f"📊 Dashboard will now show metrics for tenant: {tenant.name}")
    print(f"🔑 Login with: admin / admin123")
    print(f"🌐 Access API: http://localhost:8000/api/finance/dashboard/3d-metrics/")

if __name__ == '__main__':
    create_sample_data()
