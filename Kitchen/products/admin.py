from django.contrib import admin
from .models import Product, ProductCategory, ProductFeature, ProductVariant, ProductVariantImage


# Register your models here.

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductFeature)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantImage)
