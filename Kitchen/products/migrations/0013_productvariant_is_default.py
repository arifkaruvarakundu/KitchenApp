# Generated by Django 5.2 on 2025-06-08 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_rename_is_degault_productvariantimage_is_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
