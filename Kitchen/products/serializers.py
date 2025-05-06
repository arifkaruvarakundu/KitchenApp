from rest_framework import serializers
from .models import Product, ProductFeature, ProductVariant, ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'category_name_ar', 'category_image']

class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['key', 'value']


class ProductSerializer(serializers.ModelSerializer):
    features = ProductFeatureSerializer(many=True)
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_name_ar', 'description', 'description_ar', 'features', 'category', "use_and_care", 'use_and_care_ar']

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