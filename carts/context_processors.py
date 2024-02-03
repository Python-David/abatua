from django.core.exceptions import ObjectDoesNotExist

from carts.models import Cart, CartItem
from carts.views import get_cart_id


def menu_links(request):
    total_quantity = 0

    # Check if the user is logged in
    if request.user.is_authenticated:
        # Fetch cart items associated with the user
        user_cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total_quantity = sum(item.quantity for item in user_cart_items)

    else:
        # For guests, fetch cart items based on the session ID
        cart_id = get_cart_id(request)
        if cart_id:
            try:
                cart = Cart.objects.get(cart_id=cart_id)
                session_cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                total_quantity = sum(item.quantity for item in session_cart_items)
            except Cart.DoesNotExist:
                total_quantity = 0

    return {"cart_item_count": total_quantity}

