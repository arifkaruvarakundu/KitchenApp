from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Invoice, Order

@receiver(post_save, sender=Order)
def create_invoice_when_status_is_valid(sender, instance, created, **kwargs):
    # Avoid creating invoice if status is 'Pending' or 'Cancelled'
    if instance.status in [Order.Status.PENDING, Order.Status.CANCELLED]:
        return

    # Create invoice only if one doesn't already exist
    if not hasattr(instance, 'invoice'):
        total = instance.total_amount()
        if total > 0:
            Invoice.objects.create(
                order=instance,
                due_date=timezone.now().date(),
                total_amount=total
            )
