from django.shortcuts import render

from .models import Product


def store(request):
    products = Product.objects.all().filter(is_available=True)
    product_count = len(products)

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)
