from modeltranslation.translator import register, TranslationOptions
from .models import ProductCategory, Product, ProductFeature, ProductVariant

@register(ProductCategory)
class ProductTranslationOptions(TranslationOptions):
    fields = ('category_name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'description', 'use_and_care', 'brand')

@register(ProductFeature)
class ProductTranslationOptions(TranslationOptions):
    fields = ('key', 'value')

@register(ProductVariant)
class ProductTranslationOptions(TranslationOptions):
    fields = ('color',)