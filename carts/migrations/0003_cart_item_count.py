# Generated by Django 5.0.1 on 2024-01-27 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0002_rename_cart_item_cartitem_quantity"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="item_count",
            field=models.IntegerField(default=0),
        ),
    ]
