from django.db import models
from authentication.models import User
from django.utils import timezone
from products.models import ProductVariant

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        CONFIRMED = 'Order Confirmed', 'Order Confirmed'
        OUT_FOR_DELIVERY = 'Out for Delivery', 'Out for Delivery'
        CANCELLED = 'Cancelled', 'Cancelled'
        DELIVERED = 'Delivered', 'Delivered'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def total_amount(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name} {self.user.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product_variant.price * self.quantity

    def __str__(self):
        return f"{self.product_variant.product.product_name} x {self.quantity}"
