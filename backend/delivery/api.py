from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from accounts.permissions import RolesAllowed
from .models import Delivery, DeliveryPersonnel, Address, ShippingFeeRule
from .serializers import (
    DeliverySerializer, DeliveryPersonnelSerializer, 
    AddressSerializer, ShippingFeeRuleSerializer
)


class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']
    allowed_action_roles = {
        'list': ['owner', 'admin', 'manager', 'cashier'],
        'retrieve': ['owner', 'admin', 'manager', 'cashier'],
        'assign': ['owner', 'admin', 'manager'],
        'mark_picked_up': ['owner', 'admin', 'manager'],
        'mark_in_transit': ['owner', 'admin', 'manager'],
        'mark_delivered': ['owner', 'admin', 'manager'],
        'mark_failed': ['owner', 'admin', 'manager'],
    }

    def get_queryset(self):
        user = self.request.user
        qs = Delivery.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign a delivery person to this delivery."""
        delivery = self.get_object()
        delivery_person_id = request.data.get('delivery_person_id')
        if not delivery_person_id:
            return Response({'error': 'delivery_person_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery_person = DeliveryPersonnel.objects.get(id=delivery_person_id, tenant=delivery.tenant)
            delivery.assign(delivery_person)
            return Response(DeliverySerializer(delivery).data)
        except DeliveryPersonnel.DoesNotExist:
            return Response({'error': 'Delivery person not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def mark_picked_up(self, request, pk=None):
        """Mark delivery as picked up."""
        delivery = self.get_object()
        delivery.mark_picked_up()
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'])
    def mark_in_transit(self, request, pk=None):
        """Mark delivery as in transit."""
        delivery = self.get_object()
        delivery.mark_in_transit()
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark delivery as delivered."""
        delivery = self.get_object()
        delivery.mark_delivered()
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark delivery as failed."""
        delivery = self.get_object()
        delivery.mark_failed()
        return Response(DeliverySerializer(delivery).data)


class DeliveryPersonnelViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryPersonnelSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager']

    def get_queryset(self):
        user = self.request.user
        qs = DeliveryPersonnel.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin', 'manager', 'cashier']

    def get_queryset(self):
        user = self.request.user
        qs = Address.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)


class ShippingFeeRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingFeeRuleSerializer
    permission_classes = [RolesAllowed]
    allowed_roles = ['owner', 'admin']

    def get_queryset(self):
        user = self.request.user
        qs = ShippingFeeRule.objects.all()
        if user.is_superuser:
            return qs
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)

