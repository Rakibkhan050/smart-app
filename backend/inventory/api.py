from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer


from accounts.permissions import RolesAllowed


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [RolesAllowed]
    # Owners/Admin/Manager can CRUD products; cashiers can only read
    allowed_roles = ['owner', 'admin', 'manager', 'cashier']
    allowed_action_roles = {
        'create': ['owner', 'admin', 'manager'],
        'update': ['owner', 'admin', 'manager'],
        'partial_update': ['owner', 'admin', 'manager'],
        'destroy': ['owner', 'admin'],
    }

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)
