from .models import *
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

class InvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = ['id', 'order_id', 'customer_name', 'customer_email', 'due_date', 'total_amount', 'items']

    def get_customer_name(self, obj):
        return f"{obj.order.user.first_name} {obj.order.user.last_name}"

    def get_customer_email(self, obj):
        return obj.order.user.email

    def get_items(self, obj):
        return OrderItemSerializer(obj.order.items.all(), many=True).data

class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_name', 'status', 'created_at', 'updated_at', 'total']

    def get_total(self, obj):
        return obj.total_amount()

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'