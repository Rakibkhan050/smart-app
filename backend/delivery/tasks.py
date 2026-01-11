"""
Celery tasks for delivery automation and notifications.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    retry_backoff=True,
    retry_jitter=True
)
def notify_delivery_status_change(self, delivery_id, old_status, new_status):
    """
    Send notifications when delivery status changes.
    Notifies customer and delivery personnel.
    
    Args:
        delivery_id: Delivery record ID
        old_status: Previous status
        new_status: New status
    """
    try:
        from delivery.models import Delivery
        
        delivery = Delivery.objects.select_related(
            'delivery_person', 'address', 'tenant'
        ).get(id=delivery_id)
        
        # Status messages
        status_messages = {
            'pending': 'Your delivery has been created and is awaiting assignment.',
            'assigned': f'Your delivery has been assigned to {delivery.delivery_person.name if delivery.delivery_person else "a driver"}.',
            'picked_up': 'Your package has been picked up and is on its way!',
            'in_transit': 'Your package is in transit to your location.',
            'delivered': 'Your package has been delivered successfully!',
            'failed': 'Unfortunately, delivery failed. We will contact you shortly.',
        }
        
        # Notify customer (via order)
        customer_email = None
        try:
            # Find order by order_reference
            from pos.models import Order
            order = Order.objects.filter(
                tenant=delivery.tenant
            ).select_related('customer').first()
            
            # Try to match by ID in order_reference (e.g., "ORD-123")
            if delivery.order_reference:
                try:
                    order_id = int(delivery.order_reference.split('-')[-1])
                    order = Order.objects.filter(
                        id=order_id,
                        tenant=delivery.tenant
                    ).select_related('customer').first()
                except (ValueError, IndexError):
                    pass
            
            if order and order.customer:
                customer = order.customer
                customer_email = customer.email
                
                if customer_email:
                    subject = f"Delivery Update - {delivery.tracking_number}"
                    message = f"""
Dear Customer,

Your delivery status has been updated:

Tracking Number: {delivery.tracking_number}
Status: {new_status.upper()}

{status_messages.get(new_status, 'Your delivery status has changed.')}

Expected Delivery: {delivery.expected_delivery or 'TBD'}
Delivery Address: {delivery.address.line1 if delivery.address else 'N/A'}

Thank you for your business!
"""
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer_email],
                        fail_silently=True
                    )
                    
                    logger.info(f"Customer email sent for delivery {delivery_id} status change: {old_status} -> {new_status}")
        except Exception as e:
            logger.warning(f"Could not notify customer for delivery {delivery_id}: {e}")
        
        # Notify delivery personnel
        if delivery.delivery_person and new_status in ['assigned', 'picked_up']:
            try:
                # Find user account for delivery person if exists
                # Assuming delivery person might have a User account linked by email/phone
                personnel_users = User.objects.filter(
                    tenant=delivery.tenant,
                    email=delivery.delivery_person.phone  # Simplified - might need better matching
                )[:1]
                
                for user in personnel_users:
                    Notification.objects.create(
                        recipient=user,
                        title=f"Delivery Assignment - {delivery.tracking_number}",
                        body=f"New delivery assigned. Address: {delivery.address.line1 if delivery.address else 'N/A'}",
                        channel='in_app',
                        data={
                            'delivery_id': delivery_id,
                            'tracking_number': delivery.tracking_number
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not notify delivery person: {e}")
        
        # Notify tenant managers for failed deliveries
        if new_status == 'failed':
            try:
                managers = User.objects.filter(
                    tenant=delivery.tenant,
                    role__in=['owner', 'admin', 'manager'],
                    is_active=True
                )
                
                for manager in managers:
                    Notification.objects.create(
                        recipient=manager,
                        title=f"Delivery Failed - {delivery.tracking_number}",
                        body=f"Delivery failed for order. Please review and take action.",
                        channel='email',
                        data={
                            'delivery_id': delivery_id,
                            'tracking_number': delivery.tracking_number
                        }
                    )
                    
                    if manager.email:
                        send_mail(
                            subject=f"Delivery Failed - {delivery.tracking_number}",
                            message=f"Delivery {delivery.tracking_number} has failed. Please review the details and take appropriate action.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[manager.email],
                            fail_silently=True
                        )
            except Exception as e:
                logger.error(f"Failed to notify managers about failed delivery: {e}")
        
        return {
            'status': 'success',
            'delivery_id': delivery_id,
            'old_status': old_status,
            'new_status': new_status,
            'customer_notified': bool(customer_email)
        }
        
    except Exception as e:
        logger.error(f"Delivery notification failed for {delivery_id}: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 120},
    retry_backoff=True
)
def check_overdue_deliveries(self):
    """
    Check for deliveries that are overdue and send alerts.
    Run periodically (e.g., daily) to identify stuck deliveries.
    """
    from django.utils import timezone
    from datetime import timedelta
    from delivery.models import Delivery
    
    try:
        today = timezone.now().date()
        
        # Find deliveries that are overdue (expected_delivery in past, not delivered/failed)
        overdue_deliveries = Delivery.objects.filter(
            expected_delivery__lt=today,
            status__in=['assigned', 'picked_up', 'in_transit']
        ).select_related('tenant', 'delivery_person')
        
        overdue_count = overdue_deliveries.count()
        logger.info(f"Found {overdue_count} overdue deliveries")
        
        if overdue_count == 0:
            return {'status': 'success', 'overdue_count': 0}
        
        # Group by tenant
        tenants = {}
        for delivery in overdue_deliveries:
            tenant = delivery.tenant
            if tenant not in tenants:
                tenants[tenant] = []
            tenants[tenant].append(delivery)
        
        notifications_sent = 0
        
        # Notify managers for each tenant
        for tenant, deliveries in tenants.items():
            managers = User.objects.filter(
                tenant=tenant,
                role__in=['owner', 'admin', 'manager'],
                is_active=True
            )
            
            delivery_list = "\n".join([
                f"- {d.tracking_number}: Expected {d.expected_delivery}, Status: {d.status}"
                for d in deliveries
            ])
            
            for manager in managers:
                try:
                    Notification.objects.create(
                        recipient=manager,
                        title=f"Overdue Deliveries Alert: {len(deliveries)} deliveries",
                        body=f"The following deliveries are overdue:\n\n{delivery_list}\n\nPlease review and update status.",
                        channel='email',
                        data={
                            'overdue_count': len(deliveries),
                            'delivery_ids': [d.id for d in deliveries]
                        }
                    )
                    notifications_sent += 1
                    
                    if manager.email:
                        send_mail(
                            subject=f"Overdue Deliveries Alert - {len(deliveries)} items",
                            message=f"Overdue deliveries:\n\n{delivery_list}",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[manager.email],
                            fail_silently=True
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to notify manager about overdue deliveries: {e}")
        
        return {
            'status': 'success',
            'overdue_count': overdue_count,
            'notifications_sent': notifications_sent
        }
        
    except Exception as e:
        logger.error(f"Overdue delivery check failed: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_delivery_eta_update(self, delivery_id, estimated_minutes):
    """
    Send ETA update to customer for in-transit deliveries.
    Can be triggered by delivery tracking system or manually.
    
    Args:
        delivery_id: Delivery ID
        estimated_minutes: Estimated time in minutes until delivery
    """
    try:
        from delivery.models import Delivery
        
        delivery = Delivery.objects.select_related('address').get(id=delivery_id)
        
        if delivery.status not in ['picked_up', 'in_transit']:
            logger.warning(f"Delivery {delivery_id} not in transit, skipping ETA update")
            return {'status': 'skipped', 'reason': 'not_in_transit'}
        
        # Get customer email from related order
        customer_email = None
        try:
            # Find order by order_reference
            from pos.models import Order
            if delivery.order_reference:
                try:
                    order_id = int(delivery.order_reference.split('-')[-1])
                    order = Order.objects.filter(
                        id=order_id,
                        tenant=delivery.tenant
                    ).select_related('customer').first()
                    
                    if order and order.customer:
                        customer_email = order.customer.email
                except (ValueError, IndexError):
                    pass
        except Exception as e:
            logger.warning(f"Could not find order for delivery {delivery_id}: {e}")
        
        if not customer_email:
            return {'status': 'skipped', 'reason': 'no_customer_email'}
        
        # Send ETA notification
        hours = estimated_minutes // 60
        mins = estimated_minutes % 60
        eta_text = f"{hours}h {mins}m" if hours > 0 else f"{mins} minutes"
        
        subject = f"Your delivery is on its way! - {delivery.tracking_number}"
        message = f"""
Hello!

Good news! Your delivery is on its way and will arrive in approximately {eta_text}.

Tracking Number: {delivery.tracking_number}
Delivery Address: {delivery.address.line1 if delivery.address else 'N/A'}
Status: {delivery.status.upper()}

Please ensure someone is available to receive the package.

Thank you!
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            fail_silently=False
        )
        
        logger.info(f"ETA update sent for delivery {delivery_id}: {estimated_minutes} minutes")
        
        return {
            'status': 'success',
            'delivery_id': delivery_id,
            'estimated_minutes': estimated_minutes,
            'customer_notified': True
        }
        
    except Exception as e:
        logger.error(f"ETA update failed for delivery {delivery_id}: {e}")
        raise
