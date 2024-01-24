from django.shortcuts import render, get_list_or_404

from category.models import Category
from store.models import Product


def home(request):
    products = get_list_or_404(Product, is_available=True)
    categories = get_list_or_404(Category)

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)
