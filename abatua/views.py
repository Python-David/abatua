from django.shortcuts import render, get_list_or_404

from category.models import Category
from store.models import Product


def home(request):
    products = get_list_or_404(Product, is_available=True)

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)
