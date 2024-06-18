# Generated by Django 5.0.1 on 2024-06-17 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_rename_product_prize_orderproduct_product_price_and_more"),
        ("store", "0003_variation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderproduct",
            name="variation",
        ),
        migrations.AddField(
            model_name="orderproduct",
            name="variations",
            field=models.ManyToManyField(blank=True, to="store.variation"),
        ),
    ]