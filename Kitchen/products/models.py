from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.db.models import Q

# Create your models here.
class ProductCategory(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    category_image = models.ImageField(upload_to='categories/', null=True)
    slug = models.SlugField(unique=True, blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.category_name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name
    
class Product(models.Model):
    product_name = models.CharField(max_length=200, db_index=True)
    brand = models.CharField(max_length=100, null=True, blank=True, help_text="Enter brand name", default="ecoco")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3, db_index=True, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    use_and_care = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         base_slug = slugify(self.product_name)
    #         slug = base_slug
    #         counter = 1
    #         # Ensure slug uniqueness
    #         while Product.objects.filter(slug=slug).exists():
    #             slug = f"{base_slug}-{counter}"
    #             counter += 1
    #         self.slug = slug
    #     super().save(*args, **kwargs)

    # def get_url(self):
    #     return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    stock = models.IntegerField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Enter discount as a percentage (e.g., 20 for 20%)")
    is_available = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product'], condition=Q(is_default=True), name='only_one_default_variant_per_product')
        ]

    def __str__(self):
        variant_details = []
        if self.color:
            variant_details.append(f"Color: {self.color}")
        if self.size:
            variant_details.append(f"Size: {self.size}")

        return f"{self.id} - {self.product.product_name} - {' | '.join(variant_details)}"

class ProductVariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name="variant_images", on_delete=models.CASCADE, null=True, blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    public_id = models.CharField(max_length=255, default="", null=True, blank=True)  # Store the public_id for Cloudinary images
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            if self.variant:
                # Unset other default images for the same variant
                ProductVariantImage.objects.filter(variant=self.variant, is_default=True).exclude(pk=self.pk).update(is_default=False)
            elif self.product:
                # Unset other default images for the product (if no variant)
                ProductVariantImage.objects.filter(product=self.product, is_default=True).exclude(pk=self.pk).update(is_default=False)
        ...
        super().save(*args, **kwargs)


    def __str__(self):
        if self.variant:
            return f"Image for {self.variant.product.product_name} - Variant: {self.variant}"
        elif self.product:
            return f"Image for {self.product.product_name}"
        return "Unlinked Image"
    

