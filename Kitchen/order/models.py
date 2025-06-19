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
        if self.product_variant.price is None:
            return 0
        return self.product_variant.price * self.quantity


    def __str__(self):
        return f"{self.product_variant.product.product_name} x {self.quantity}"

class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.first_name} {self.user.last_name} - {self.message}"

class Invoice(models.Model):
    order = models.OneToOneField(Order, related_name="invoice", on_delete=models.CASCADE, null=True, blank=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice for Order #{self.order.id}"
