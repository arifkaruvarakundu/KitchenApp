from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, ProductCategory

@receiver(pre_save, sender=ProductCategory)
def set_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.category_name)

@receiver(pre_save, sender=Product)
def set_product_slug(sender, instance, **kwargs):
    if not instance.slug:
        base_slug = slugify(instance.product_name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug
