from rest_framework import serializers
from .models import Product, ProductFeature, ProductVariant, ProductCategory, ProductVariantImage

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'category_name_ar', 'category_image']

class ProductCategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory  # or whatever your Category model is named
        fields = ['id', 'category_name']

class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['key', 'value', 'key_ar', 'value_ar']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'color','color_ar', 'size', 'price', 'stock', 'is_available']

class ProductVariantImageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image']


class ProductVariantImageSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image', 'public_id', 'variant']


class ProductListSerializer(serializers.ModelSerializer):
    default_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = ProductCategoryMinimalSerializer()
    default_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name','product_name_ar', 'default_image', 'price', 'category', 'default_variant']

    def get_default_image(self, obj):
        default_image = obj.product_images.filter(is_default=True).first()
        if not default_image:
            default_image = obj.product_images.first()
        return ProductVariantImageMinimalSerializer(default_image).data if default_image else None

    def get_price(self, obj):
        variants = obj.variants.all()
        if not variants.exists():
            return obj.price

        variant_prices = set(v.price for v in variants if v.price is not None)

        if len(variant_prices) == 1:
            return variant_prices.pop()

        default_image = obj.product_images.filter(is_default=True).first() or obj.product_images.first()
        if default_image and default_image.variant and default_image.variant.price:
            return default_image.variant.price

        return obj.price or None

    def get_default_variant(self, obj):
        default_variant = obj.variants.filter(is_default=True).first()
        if default_variant:
            return default_variant.id
        return None

class ProductSerializer(serializers.ModelSerializer):
    features = ProductFeatureSerializer(many=True)
    category = ProductCategorySerializer()
    product_images = ProductVariantImageSerializer(many=True, read_only=True)
    variant_images = ProductVariantImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    default_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()  # Override price

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_name_ar', 'brand',
            'price',  # <- from get_price
            'description', 'description_ar',
            'features', 'category',
            "use_and_care", 'use_and_care_ar',
            'product_images', 'variant_images',
            'variants', 'default_image'
        ]

    def get_default_image(self, obj):
        default_image = obj.product_images.filter(is_default=True).first()
        if not default_image:
            default_image = obj.product_images.first()
        return ProductVariantImageSerializer(default_image).data if default_image else None

    def get_price(self, obj):
        variants = obj.variants.all()

        # No variants → return product price
        if not variants.exists():
            return obj.price

        variant_prices = set(v.price for v in variants if v.price is not None)

        # If all variants have same price
        if len(variant_prices) == 1:
            return variant_prices.pop()

        # If variants have different prices, return the one matching the default image (if linked)
        default_image = obj.product_images.filter(is_default=True).first() or obj.product_images.first()
        if default_image and default_image.variant and default_image.variant.price:
            return default_image.variant.price

        # Fallback
        return obj.price or None

    
