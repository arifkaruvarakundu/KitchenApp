from django.contrib import admin
from .models import *

# ✅ Inline for displaying OrderItems inside Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_price', 'quantity', 'item_total')
    can_delete = False

    def product_name(self, obj):
        return obj.product_variant.product.product_name

    def variant_price(self, obj):
        return obj.product_variant.price

    def item_total(self, obj):
        return obj.total_price()

# ✅ Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_full_name', 'status', 'created_at', 'total_amount_display')
    inlines = [OrderItemInline]  # ✅ Now it's defined above

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def total_amount_display(self, obj):
        return obj.total_amount()

# ✅ Register the models with admin
admin.site.register(Order, OrderAdmin)

# ✅ Optional: Separate admin for individual OrderItem view
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'order_id', 'variant_price', 'quantity', 'item_total')

    def product_name(self, obj):
        return obj.product_variant.product.product_name

    def order_id(self, obj):
        return obj.order.id

    def variant_price(self, obj):
        return obj.product_variant.price

    def item_total(self, obj):
        return obj.total_price()

admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Notification)
admin.site.register(Invoice)