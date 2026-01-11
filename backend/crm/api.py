from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, LoyaltyPoint, Supplier, LoyaltyTransaction, PurchaseHistory
from .serializers import (
    CustomerSerializer, LoyaltyPointSerializer, SupplierSerializer,
    LoyaltyTransactionSerializer, PurchaseHistorySerializer
)
from accounts.permissions import RolesAllowed


class IsTenantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class TenantScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantOwner]

    def get_tenant(self):
        user = self.request.user
        if user.is_superuser:
            return None
        return getattr(user, 'tenant', None)

    def filter_by_tenant(self, qs):
        tenant = self.get_tenant()
        if tenant is None and not self.request.user.is_superuser:
            return qs.none()
        if tenant is None:
            return qs
        return qs.filter(tenant=tenant)


class CustomerViewSet(TenantScopedViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager', 'cashier']

    def get_queryset(self):
        return self.filter_by_tenant(Customer.objects.all())

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)

    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        """Get purchase history for a specific customer."""
        customer = self.get_object()
        purchases = customer.purchases.all()
        serializer = PurchaseHistorySerializer(purchases, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def loyalty_transactions(self, request, pk=None):
        """Get loyalty transaction history for a specific customer."""
        customer = self.get_object()
        transactions = customer.loyalty_transactions.all()
        serializer = LoyaltyTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class LoyaltyPointViewSet(viewsets.ModelViewSet):
    serializer_class = LoyaltyPointSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        qs = LoyaltyPoint.objects.select_related('customer').all()
        # LoyaltyPoints tie to customers which are tenant-scoped via customer. Filter via related customer.
        tenant = self.get_tenant() if hasattr(self, 'get_tenant') else getattr(self.request.user, 'tenant', None)
        if tenant is None and not self.request.user.is_superuser:
            return qs.none()
        if tenant is None:
            return qs
        return qs.filter(customer__tenant=tenant)

    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        """Redeem loyalty points."""
        loyalty = self.get_object()
        points = request.data.get('points', 0)
        reason = request.data.get('reason', 'Manual redemption')

        try:
            points = int(points)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid points value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if points <= 0:
            return Response(
                {'error': 'Points must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if loyalty.points < points:
            return Response(
                {'error': f'Insufficient points. Available: {loyalty.points}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction = loyalty.redeem_points(points, reason=reason)
        if transaction:
            return Response({
                'success': True,
                'remaining_points': loyalty.points,
                'transaction': LoyaltyTransactionSerializer(transaction).data
            })
        else:
            return Response(
                {'error': 'Failed to redeem points'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """Manually add loyalty points (admin only)."""
        loyalty = self.get_object()
        points = request.data.get('points', 0)
        reason = request.data.get('reason', 'Manual adjustment')

        try:
            points = int(points)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid points value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if points <= 0:
            return Response(
                {'error': 'Points must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction = loyalty.add_points(points, reason=reason)
        if transaction:
            return Response({
                'success': True,
                'total_points': loyalty.points,
                'transaction': LoyaltyTransactionSerializer(transaction).data
            })
        else:
            return Response(
                {'error': 'Failed to add points'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoyaltyTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for loyalty transaction history."""
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        qs = LoyaltyTransaction.objects.select_related('customer').all()
        # Filter by tenant via customer relationship
        tenant = getattr(self.request.user, 'tenant', None)
        if tenant is None and not self.request.user.is_superuser:
            return qs.none()
        if tenant is None:
            return qs
        return qs.filter(customer__tenant=tenant)


class PurchaseHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for purchase history."""
    serializer_class = PurchaseHistorySerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager', 'cashier']

    def get_queryset(self):
        qs = PurchaseHistory.objects.select_related('customer', 'order').all()
        # Filter by tenant via customer relationship
        tenant = getattr(self.request.user, 'tenant', None)
        if tenant is None and not self.request.user.is_superuser:
            return qs.none()
        if tenant is None:
            return qs
        return qs.filter(customer__tenant=tenant)


class SupplierViewSet(TenantScopedViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        return self.filter_by_tenant(Supplier.objects.all())

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)

