from django.core.exceptions import ObjectDoesNotExist

from carts.models import Cart, CartItem
from carts.views import get_cart_id


def menu_links(request):

    total_quantity = 0
    cart_id = get_cart_id(request)
    if cart_id:
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            total_quantity = sum(item.quantity for item in cart_items)
        except ObjectDoesNotExist:
            total_quantity = 0

    return {"cart_item_count": total_quantity}
