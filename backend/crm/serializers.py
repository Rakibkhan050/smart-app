from rest_framework import serializers
from .models import Customer, LoyaltyPoint, Supplier, LoyaltyTransaction, PurchaseHistory


class CustomerSerializer(serializers.ModelSerializer):
    loyalty_points = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'loyalty_points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'loyalty_points', 'created_at', 'updated_at']
    
    def get_loyalty_points(self, obj):
        """Include current loyalty points in customer data."""
        try:
            return obj.loyalty.points
        except LoyaltyPoint.DoesNotExist:
            return 0


class LoyaltyPointSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyPoint
        fields = ['id', 'customer', 'customer_name', 'points', 'updated_at']
        read_only_fields = ['id', 'updated_at']
    
    def get_customer_name(self, obj):
        return str(obj.customer)


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'customer', 'customer_name', 'transaction_type', 'points', 'reason', 'reference_order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_customer_name(self, obj):
        return str(obj.customer)


class PurchaseHistorySerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseHistory
        fields = ['id', 'customer', 'customer_name', 'order', 'order_status', 'amount', 'loyalty_earned', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_customer_name(self, obj):
        return str(obj.customer)
    
    def get_order_status(self, obj):
        return obj.order.status if obj.order else None


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact', 'phone', 'email', 'payment_status', 'created_at']
        read_only_fields = ['id', 'created_at']
