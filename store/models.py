from decimal import Decimal

from django.db import models
from django.urls import reverse

from accounts.models import Account
from category.models import Category

from .config import VARIATION_CATEGORY_CHOICES


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    image = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def get_average_rating(self):
        result = ReviewRating.objects.filter(product=self, status=True).aggregate(
            average_rating=models.Avg("rating")
        )
        average = 0
        if result["average_rating"] is not None:
            average = float(result["average_rating"])
        return average

    def count_review(self):
        result = ReviewRating.objects.filter(product=self, status=True).aggregate(
            count=models.Count("id")
        )
        count = 0
        if result["count"] is not None:
            count = int(result["count"])
        return count


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category="size", is_active=True
        )


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=VARIATION_CATEGORY_CHOICES
    )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_category} - {self.variation_value}"


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=100, blank=True)
    rating = models.FloatField()
    ip_address = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products", max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = "productgallery"
        verbose_name_plural = "product gallery"
