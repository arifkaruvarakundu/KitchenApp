from rest_framework import serializers
from django.utils.text import slugify
from .models import Product, ProductFeature, ProductVariant, ProductCategory, ProductVariantImage

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'category_name_ar', 'category_image']
        read_only_fields = ['slug']

    def update(self, instance, validated_data):
        instance.category_name = validated_data.get('category_name', instance.category_name)
        if 'category_image' in validated_data:
            instance.category_image = validated_data['category_image']
        instance.slug = slugify(instance.category_name)
        instance.save()
        return instance

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
        fields = ['id', 'product', 'color','color_ar', 'size', 'price','discount_percentage', 'is_default', 'stock', 'is_available']

class ProductVariantImageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image']


class ProductVariantImageSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image', 'public_id', 'variant', 'is_default']


class ProductListSerializer(serializers.ModelSerializer):
    default_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = ProductCategoryMinimalSerializer()
    default_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name','product_name_ar', 'default_image', 'price', 'is_active', 'category', 'default_variant']

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
            "use_and_care", 'use_and_care_ar', 'is_active',
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


# class ProductVariantImageCreateSerializer(serializers.Serializer):
#     image = serializers.ImageField()

#     def create(self, validated_data):
#         return validated_data  # We'll handle Cloudinary in the view

# class ProductVariantCreateSerializer(serializers.Serializer):
#     color = serializers.CharField(required=False, allow_blank=True)
#     color_ar = serializers.CharField(required=False, allow_blank=True)
#     size = serializers.CharField(required=False, allow_blank=True)
#     price = serializers.DecimalField(max_digits=10, decimal_places=3)
#     stock = serializers.IntegerField()
#     is_available = serializers.BooleanField(default=True)
#     is_default = serializers.BooleanField(default=False)
#     images = ProductVariantImageCreateSerializer(many=True, required=False)

#     def validate_price(self, value):
#         if value < 0:
#             raise serializers.ValidationError("Price must be non-negative")
#         return value

# class ProductCreateSerializer(serializers.Serializer):
#     product_name = serializers.CharField()
#     product_name_ar = serializers.CharField()
#     description = serializers.CharField(required=False, allow_blank=True)
#     description_ar = serializers.CharField(required=False, allow_blank=True)
#     use_and_care = serializers.CharField(required=False, allow_blank=True)
#     use_and_care_ar = serializers.CharField(required=False, allow_blank=True)
#     category = serializers.IntegerField()
#     is_available = serializers.BooleanField(default=True)
#     is_default = serializers.BooleanField(default=False)

#     variants = ProductVariantCreateSerializer(many=True)

#     def validate_category(self, value):
#         if not ProductCategory.objects.filter(id=value).exists():
#             raise serializers.ValidationError("Invalid category ID")
#         return value

#     def create(self, validated_data):
#         variants_data = validated_data.pop("variants", [])
#         category = ProductCategory.objects.get(id=validated_data.pop("category"))

#         product = Product.objects.create(category=category, **validated_data)

#         for variant_data in variants_data:
#             images_data = variant_data.pop("images", [])
#             variant = ProductVariant.objects.create(product=product, **variant_data)

#             for image_data in images_data:
#                 image = image_data["image"]
#                 upload_result = cloudinary.uploader.upload(image)
#                 ProductVariantImage.objects.create(
#                     product=product,
#                     variant=variant,
#                     image=upload_result["secure_url"],
#                     public_id=upload_result["public_id"],
#                 )

#         return product

