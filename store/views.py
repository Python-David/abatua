from django.shortcuts import render, get_list_or_404

from category.models import Category
from .models import Product


def store(request, category_slug=None):
    if category_slug:
        categories = get_list_or_404(Category, slug=category_slug)
        products = get_list_or_404(Product, is_available=True, category__in=categories)
    else:
        products = Product.objects.filter(is_available=True)

    product_count = len(products)

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

