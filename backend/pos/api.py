from rest_framework import viewsets, permissions, decorators, response
from .models import Order
from .serializers import OrderSerializer
from receipts.tasks import generate_receipt_for_payment


from accounts.permissions import RolesAllowed


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [RolesAllowed]
    # allow owners/admins/managers/cashiers to manage orders (cashiers allowed to create/pay)
    allowed_roles = ['owner', 'admin', 'manager', 'cashier']
    allowed_action_roles = {
        'pay': ['cashier', 'manager', 'admin', 'owner'],
        'create': ['cashier', 'manager', 'admin', 'owner'],
    }

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        order = serializer.save(tenant=tenant)
        return order

    @decorators.action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        # mark paid (creates Payment and updates inventory)
        p = order.mark_paid(provider=request.data.get('provider', 'visa_mastercard'))

        # enqueue receipt generation; if delay fails, try synchronous fallback
        try:
            generate_receipt_for_payment.delay(payment_id=p.payment_id, amount=str(p.amount), currency=getattr(p, 'currency', 'SAR'))
        except Exception:
            func = getattr(generate_receipt_for_payment, '__wrapped__', None)
            if func:
                try:
                    # call underlying function synchronously (first arg is `self` for bound task)
                    func(None, payment_id=p.payment_id, amount=float(p.amount), currency=getattr(p, 'currency', 'SAR'))
                except Exception:
                    pass

        return response.Response({'status': 'paid', 'payment_id': p.payment_id})