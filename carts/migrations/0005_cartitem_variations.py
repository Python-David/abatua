# Generated by Django 5.0.1 on 2024-01-31 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_remove_cart_item_count'),
        ('store', '0003_variation'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variations',
            field=models.ManyToManyField(blank=True, to='store.variation'),
        ),
    ]