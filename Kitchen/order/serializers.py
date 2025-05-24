from .models import OrderItem, Order
from products.serializers import ProductVariantSerializer
from products.models import ProductVariant
from rest_framework import serializers

class ProductVariantColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['color']  # Only include color

class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantColorSerializer(read_only=True)
    price = serializers.DecimalField(source='product_variant.price', max_digits=10, decimal_places=3, read_only=True)
    product = serializers.CharField(source='product_variant.product.product_name', read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['product','product_variant','price', 'quantity', 'total_price']

class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'items_count', 'total_amount']
    def get_items_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'updated_at', 'total_amount', 'items']