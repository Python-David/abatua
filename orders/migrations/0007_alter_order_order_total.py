# Generated by Django 5.0.1 on 2024-06-18 15:49

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0006_alter_order_tax"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_total",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=10
            ),
        ),
    ]