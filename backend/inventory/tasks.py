from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, Q
from decimal import Decimal
from .models import Product
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def check_low_stock_and_notify(self):
    """
    Find low stock products and notify tenant admins/managers.
    Runs periodically to check inventory levels and send alerts.
    
    Retry strategy:
    - Max 3 retries
    - Exponential backoff starting at 60s
    - Max backoff 600s (10 minutes)
    - Jitter to prevent thundering herd
    """
    User = get_user_model()
    
    try:
        # Find products where quantity is at or below threshold
        low_products = Product.objects.filter(
            quantity__lte=F('low_stock_threshold')
        ).exclude(
            low_stock_threshold=0
        ).select_related('tenant')
        
        products_count = low_products.count()
        logger.info(f"Found {products_count} products with low stock")
        
        if products_count == 0:
            return {'status': 'success', 'low_stock_count': 0}
        
        notifications_sent = 0
        emails_sent = 0
        
        # Group by tenant for efficient processing
        tenants = {}
        for product in low_products:
            tenant = product.tenant
            if tenant not in tenants:
                tenants[tenant] = []
            tenants[tenant].append(product)
        
        # Process each tenant's low stock products
        for tenant, products in tenants.items():
            # Find users to notify (managers, admins, owners)
            try:
                users = User.objects.filter(
                    tenant=tenant,
                    is_active=True
                ).filter(
                    Q(role__in=['owner', 'admin', 'manager']) | Q(is_staff=True)
                ).distinct()
            except Exception as e:
                logger.warning(f"Failed to filter users by tenant: {e}")
                users = User.objects.filter(
                    is_active=True,
                    is_staff=True
                )
            
            if not users.exists():
                logger.warning(f"No users to notify for tenant {tenant}")
                continue
            
            # Create notification summary
            product_list = "\n".join([
                f"- {p.name} (SKU: {p.sku}): {p.quantity} {p.unit} (threshold: {p.low_stock_threshold})"
                for p in products
            ])
            
            title = f"Low Stock Alert: {len(products)} product(s) need reordering"
            body = (
                f"The following products have reached their low stock threshold:\n\n"
                f"{product_list}\n\n"
                f"Please review and reorder as necessary."
            )
            
            # Send notifications
            for user in users:
                try:
                    # Create in-app notification
                    Notification.objects.create(
                        recipient=user,
                        title=title,
                        body=body,
                        channel='email',
                        data={
                            'tenant_id': tenant.id if tenant else None,
                            'product_count': len(products),
                            'product_ids': [p.id for p in products]
                        }
                    )
                    notifications_sent += 1
                    
                    # Send email
                    if user.email:
                        send_mail(
                            subject=title,
                            message=body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True
                        )
                        emails_sent += 1
                        
                except Exception as e:
                    logger.error(f"Failed to notify user {user.id}: {e}")
        
        result = {
            'status': 'success',
            'low_stock_count': products_count,
            'notifications_sent': notifications_sent,
            'emails_sent': emails_sent
        }
        
        logger.info(f"Low stock check completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Low stock check failed: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 30},
    retry_backoff=True
)
def restock_product(self, product_id, quantity, notes=''):
    """
    Task to handle product restocking.
    Can be triggered manually or automatically from purchase orders.
    """
    try:
        product = Product.objects.get(id=product_id)
        old_quantity = product.quantity
        product.quantity = Decimal(str(product.quantity)) + Decimal(str(quantity))
        product.save(update_fields=['quantity'])
        
        logger.info(
            f"Restocked product {product.name} (ID: {product_id}): "
            f"{old_quantity} -> {product.quantity} (+{quantity})"
        )
        
        # Notify relevant users if stock was previously low
        if old_quantity <= product.low_stock_threshold and product.quantity > product.low_stock_threshold:
            User = get_user_model()
            users = User.objects.filter(
                tenant=product.tenant,
                role__in=['owner', 'admin', 'manager'],
                is_active=True
            )
            
            for user in users:
                Notification.objects.create(
                    recipient=user,
                    title=f"Stock Replenished: {product.name}",
                    body=f"{product.name} has been restocked. New quantity: {product.quantity} {product.unit}",
                    channel='in_app',
                    data={'product_id': product_id}
                )
        
        return {
            'status': 'success',
            'product_id': product_id,
            'old_quantity': float(old_quantity),
            'new_quantity': float(product.quantity),
            'added': float(quantity)
        }
        
    except Product.DoesNotExist:
        logger.error(f"Product {product_id} not found for restocking")
        raise
    except Exception as e:
        logger.error(f"Failed to restock product {product_id}: {e}")
        raise
