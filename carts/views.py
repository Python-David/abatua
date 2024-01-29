from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from carts.models import Cart, CartItem
from store.models import Product


def get_cart_id(request):
    cart_id = request.session.session_key

    if not cart_id:
        cart_id = request.session.create()

    return cart_id


def cart(request, total=0, quantity=0, cart_items=None):
    total_tax = 0
    try:
        cart = get_object_or_404(Cart, cart_id=get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            # calculate total
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

            # calculate tax
            tax = cart_item.get_tax(3)
            total_tax += tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'total_tax': total_tax,
        'true_total': total + total_tax,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=get_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=get_cart_id(request),
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()

    return redirect('cart')


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=get_cart_id(request))
    cart_item = get_object_or_404(CartItem, product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=get_cart_id(request))
    cart_item = get_object_or_404(CartItem, product=product, cart=cart)

    cart_item.delete()

    return redirect('cart')



