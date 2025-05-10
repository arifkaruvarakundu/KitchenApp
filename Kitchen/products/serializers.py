from rest_framework import serializers
from .models import Product, ProductFeature, ProductVariant, ProductCategory, ProductVariantImage

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'category_name_ar', 'category_image']

class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['key', 'value']

class ProductVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image', 'public_id']


class ProductSerializer(serializers.ModelSerializer):
    features = ProductFeatureSerializer(many=True)
    category = ProductCategorySerializer()
    product_images = ProductVariantImageSerializer(many=True, read_only=True)
    variant_images = ProductVariantImageSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_name_ar', 'price', 'description', 'description_ar', 'features', 'category', "use_and_care", 'use_and_care_ar', 'product_images', 'variant_images']

    def create(self, validated_data):
        features_data = validated_data.pop('features')
        product = Product.objects.create(**validated_data)
        for feature in features_data:
            ProductFeature.objects.create(product=product, **feature)
        return product
    
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'color','color_ar', 'size', 'price', 'stock', 'is_available']