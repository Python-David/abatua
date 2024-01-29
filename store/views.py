from django.core.paginator import Paginator
from django.shortcuts import render, get_list_or_404, get_object_or_404

from carts.models import CartItem
from carts.views import get_cart_id
from category.models import Category
from .models import Product


def store(request, category_slug=None):
    if category_slug:
        categories = get_list_or_404(Category, slug=category_slug)
        products = get_list_or_404(Product, is_available=True, category__in=categories)
    else:
        products = Product.objects.filter(is_available=True)

    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = len(products)

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug=None, product_slug=None):
    try:
        product = get_object_or_404(Product, slug=product_slug)
        category = get_object_or_404(Category, slug=category_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=get_cart_id(request), product=product).exists()
    except Exception as e:
        raise e

    context = {
        'product': product,
        'category': category,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)
