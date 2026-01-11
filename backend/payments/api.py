from rest_framework import viewsets, permissions
from accounts.permissions import RolesAllowed
from crm.api import IsTenantOwner
from .models import Payment, Receipt
from .serializers import PaymentSerializer, ReceiptSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    # allow managers/admin/owner to view payments; cashiers shouldn't see payment lists
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)
    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [IsTenantOwner]

    def get_queryset(self):
        user = self.request.user
        qs = Receipt.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)
