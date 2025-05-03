from django.db import models
from django.urls import reverse

# Create your models here.
class ProductCategory(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    category_image = models.ImageField(upload_to='categories/', null=True)

    def __str__(self):
        return self.category_name
    
class Product(models.Model):
    product_name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, null=True, blank=True, help_text="Enter brand name")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    use_and_care = models.TextField(max_length=500, blank=True)
    is_available = models.BooleanField(default=True)
    
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    

    def get_url(self):
        return reverse('product_detail', args=[self.category.name, self.slug])


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
    price = models.DecimalField(max_digits=10, decimal_places=3)
    stock = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        variant_details = []
        if self.color:
            variant_details.append(f"Color: {self.color}")
        if self.size:
            variant_details.append(f"Size: {self.size}")

        return f"{self.product.product_name} - {' | '.join(variant_details)}"

class ProductVariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name="variant_images", on_delete=models.CASCADE)
    image_url = models.URLField(default="")   # Store the image in Cloudinary
    public_id = models.CharField(max_length=255, default="")  # Store the public_id for Cloudinary images
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.variant.product.product_name} - Variant: {self.variant}"
    

