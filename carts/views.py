from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from carts.models import Cart, CartItem
from store.models import Product, Variation


def get_cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def cart(request, total=0, quantity=0, cart_items=None):
    total_tax = 0
    cart_id = get_cart_id(request)
    cart_, created = Cart.objects.get_or_create(cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart_, is_active=True)

    for cart_item in cart_items:
        # Calculate total
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

        # Calculate tax
        tax = cart_item.get_tax(3)  # Assuming get_tax is a method of CartItem
        total_tax += tax

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "total_tax": total_tax,
        "true_total": total + total_tax,
    }
    return render(request, "store/cart.html", context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variations = []

    if request.method == "POST":
        # Initialize an empty dictionary to hold variation data

        # Iterate over request.POST items
        for key, value in request.POST.items():
            if (
                    key != "csrfmiddlewaretoken" and value
            ):  # Exclude CSRF token and empty fields
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    variations.append(variation)
                except:
                    pass

    try:
        cart = Cart.objects.get(cart_id=get_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=get_cart_id(request),
        )
    cart.save()

    cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        existing_variations_list = []
        id_list = []

        for item in cart_item:
            existing_variations = item.variations.all()
            existing_variations_list.append(list(existing_variations))
            id_list.append(item.id)

        if variations in existing_variations_list:
            index = existing_variations_list.index(variations)
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(variations) > 0:
                item.variations.clear()
                item.variations.add(*variations)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*variations)
        cart_item.save()

    return redirect("cart")


def remove_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=get_cart_id(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect("cart")


def remove_product(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=get_cart_id(request))

    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()

    return redirect("cart")


def checkout(request, total=0, quantity=0):
    total_tax = 0
    cart_id = get_cart_id(request)
    cart_, created = Cart.objects.get_or_create(cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart_, is_active=True)

    for cart_item in cart_items:
        # Calculate total
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

        # Calculate tax
        tax = cart_item.get_tax(3)  # Assuming get_tax is a method of CartItem
        total_tax += tax

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "total_tax": total_tax,
        "true_total": total + total_tax,
    }

    return render(request, "store/checkout.html", context)
