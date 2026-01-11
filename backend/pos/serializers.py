from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'subtotal', 'tax_amount', 'shipping_fee', 'total', 'items', 'created_at']
        read_only_fields = ['subtotal', 'total', 'created_at']

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for it in items:
            OrderItem.objects.create(order=order, product=it['product'], quantity=it.get('quantity', 1), unit_price=it.get('unit_price', it['product'].sell_price))
        order.recalc_totals()
        return order
