from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from carts.models import Cart, CartItem
from carts.views import get_cart_id


def send_email(request, user, subject, template, redirect_url):
    """
    Sends an email to the user with a custom message.
    :param request: HttpRequest object.
    :param user: User instance to whom the email is sent.
    :param subject: Subject of the email.
    :param template: Path to the template used for the email body.
    :param redirect_url: URL to redirect to after sending the email.
    """
    current_site = get_current_site(request)
    message = render_to_string(
        template,
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    email = EmailMessage(subject, message, to=[user.email])
    email.send()


def merge_cart_items(request, user):
    try:
        cart_id = get_cart_id(request)
        cart, created = Cart.objects.get_or_create(cart_id=cart_id)

        # Check if there are any cart items for the guest cart
        guest_cart_items = CartItem.objects.filter(cart=cart)
        if not guest_cart_items.exists():
            return True  # No items to merge

        for guest_item in guest_cart_items:
            product_variations = list(guest_item.variations.all())
            user_cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=guest_item.product,
                defaults={"quantity": 0},  # Prevent auto-increment
            )
            # Check for matching product variations
            if set(product_variations) == set(list(user_cart_item.variations.all())):
                user_cart_item.quantity += guest_item.quantity
            else:
                # Assign guest cart item to the user if no exact match is found
                guest_item.user = user
                guest_item.save()
                continue  # Skip the deletion for newly assigned items

            user_cart_item.save()
            guest_item.delete()  # Remove the guest item after merging

        return True
    except Exception as e:
        # Consider logging the exception e here
        return False
