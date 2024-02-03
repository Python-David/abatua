from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import Cart, CartItem
from store.models import Product, Variation


def get_cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def cart(request, total=0, quantity=0, cart_items=None):
    total_tax = 0
    cart_id = get_cart_id(request)

    if request.user.is_authenticated:
        # cart_, created = Cart.objects.get_or_create(cart_id=cart_id)
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
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
    product = Product.objects.get(id=product_id)
    current_user = None
    cart = None

    # Check if user is logged in
    if request.user.is_authenticated:
        current_user = request.user
    else:
        cart_id = get_cart_id(request)
        cart, created = Cart.objects.get_or_create(cart_id=cart_id)

    variations = []
    if request.method == "POST":
        for key, value in request.POST.items():
            if key != "csrfmiddlewaretoken" and value:
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    variations.append(variation)
                except Variation.DoesNotExist:
                    pass  # Variation does not exist

    # Check if the CartItem exists
    if current_user:
        cart_item_qs = CartItem.objects.filter(user=current_user, product=product, is_active=True)
    else:
        cart_item_qs = CartItem.objects.filter(cart=cart, product=product, is_active=True)

    cart_item_exists = False
    for item in cart_item_qs:
        if set(variations) == set(item.variations.all()):
            cart_item_exists = True
            cart_item = item
            break

    if cart_item_exists:
        # Increase the quantity of the existing cart item
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Create a new CartItem with the given product, variations, and cart or user
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart if not current_user else None,
            user=current_user
        )
        if variations:
            cart_item.variations.set(variations)
        cart_item.save()

    return redirect('cart')


def remove_from_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)

    # Determine whether to use the cart associated with the session or the user
    if request.user.is_authenticated:
        # For authenticated users, look for cart items associated with the user
        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id, is_active=True)
        except CartItem.DoesNotExist:
            pass  # Handle the case where the cart item does not exist
    else:
        # For guest users, use the session-based cart
        cart = Cart.objects.get(cart_id=get_cart_id(request))
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        except CartItem.DoesNotExist:
            pass  # Handle the case where the cart item does not exist

    # Decrement the quantity of the cart item or remove it if the quantity is 1
    try:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except NameError:
        pass  # Handle the case where cart_item is not defined due to the try-except blocks above

    return redirect("cart")


def remove_product(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)

    # Determine if the operation should be based on the user or the session cart
    if request.user.is_authenticated:
        # For authenticated users, directly target the cart item associated with the user
        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        except CartItem.DoesNotExist:
            return redirect("cart")
    else:
        # For guests, use the session-based cart
        cart = Cart.objects.get(cart_id=get_cart_id(request))
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        except CartItem.DoesNotExist:
            return redirect("cart")

    # Delete the cart item
    cart_item.delete()

    return redirect("cart")


@login_required(login_url="login")
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
