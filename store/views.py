from django.shortcuts import render, get_list_or_404, get_object_or_404

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


def product_detail(request, category_slug=None, product_slug=None):
    try:
        product = get_object_or_404(Product, slug=product_slug)
        category = get_object_or_404(Category, slug=category_slug)
    except Exception as e:
        raise e

    context = {
        'product': product,
        'category': category,
    }

    return render(request, 'store/product_detail.html', context)
