from decimal import Decimal, ROUND_HALF_UP

from django.db import models

from store.models import Product


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def get_tax(self, tax_rate: float) -> Decimal:
        tax_amount = (self.product.price * (Decimal(tax_rate) / 100)) * self.quantity
        # Round to 2 decimal places
        return tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name
