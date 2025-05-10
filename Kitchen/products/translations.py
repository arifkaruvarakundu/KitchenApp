from modeltranslation.translator import register, TranslationOptions
from .models import ProductCategory, Product, ProductFeature, ProductVariant

@register(ProductCategory)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('category_name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'description', 'use_and_care', 'brand')

@register(ProductFeature)
class ProductFeatureTranslationOptions(TranslationOptions):
    fields = ('key', 'value')

@register(ProductVariant)
class ProductVariantTranslationOptions(TranslationOptions):
    fields = ('color',)