from django.shortcuts import get_list_or_404, render

from category.models import Category
from store.models import Product, ReviewRating


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by("-date_created")
    product_reviews = {}

    for product in products:
        reviews = ReviewRating.objects.filter(product=product, status=True)
        product_reviews[product.id] = reviews

    context = {
        "products": products,
        "product_reviews": product_reviews,
    }
    return render(request, "home.html", context)

