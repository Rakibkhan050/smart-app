from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category', 'sku', 'barcode', 'unit', 'quantity', 'low_stock_threshold', 'cost_price', 'sell_price', 'profit', 'is_low_stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'profit', 'created_at', 'updated_at']
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
