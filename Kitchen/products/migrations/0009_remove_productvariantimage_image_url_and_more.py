# Generated by Django 5.2 on 2025-05-10 09:53

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_brand_ar_product_brand_en_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariantimage',
            name='image_url',
        ),
        migrations.AddField(
            model_name='productvariantimage',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
