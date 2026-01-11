from rest_framework import serializers
from .models import Delivery, DeliveryPersonnel, Address, ShippingFeeRule


class DeliveryPersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPersonnel
        fields = ['id', 'name', 'phone', 'active']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'line1', 'line2', 'city', 'country', 'latitude', 'longitude', 'zone', 'created_at']


class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = DeliveryPersonnelSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    delivery_person_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryPersonnel.objects.all(), 
        write_only=True, 
        required=False
    )
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Delivery
        fields = [
            'id', 'order_reference', 'tracking_number', 'status',
            'delivery_person', 'delivery_person_id', 'address', 'address_id',
            'fee', 'expected_delivery', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        delivery_person_id = validated_data.pop('delivery_person_id', None)
        address_id = validated_data.pop('address_id', None)
        delivery = Delivery.objects.create(**validated_data)
        if delivery_person_id:
            delivery.delivery_person_id = delivery_person_id
        if address_id:
            delivery.address_id = address_id
        delivery.save()
        return delivery

    def update(self, instance, validated_data):
        delivery_person_id = validated_data.pop('delivery_person_id', None)
        address_id = validated_data.pop('address_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if delivery_person_id is not None:
            instance.delivery_person_id = delivery_person_id
        if address_id is not None:
            instance.address_id = address_id
        instance.save()
        return instance


class ShippingFeeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingFeeRule
        fields = ['id', 'zone', 'base_fee', 'per_km_fee', 'min_distance', 'max_distance', 'created_at']
