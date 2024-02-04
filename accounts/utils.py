import requests
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect
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

        guest_cart_items = CartItem.objects.filter(cart=cart)
        if not guest_cart_items.exists():
            return True  # No items to merge

        for guest_item in guest_cart_items:
            # Get the variations of the guest item
            product_variations = set(guest_item.variations.all())

            # Try to find a matching cart item for the user
            matching_item = None
            user_cart_items = CartItem.objects.filter(
                user=user, product=guest_item.product
            )
            for item in user_cart_items:
                if product_variations == set(item.variations.all()):
                    matching_item = item
                    break

            if matching_item:
                # If a matching item is found, increment its quantity
                matching_item.quantity += guest_item.quantity
                matching_item.save()
                guest_item.delete()  # Remove the guest item after merging
            else:
                # If no matching item is found, reassign the guest item to the user
                guest_item.user = user
                guest_item.cart = None  # Remove the guest cart association
                guest_item.save()

        return True
    except Exception as e:
        # Log the exception for debugging purposes
        return False


def redirect_to_next_page(request):
    """
    Redirects the user to the 'next' page specified in the query parameters of the HTTP_REFERER.
    Uses the requests library to parse the query string. If no 'next' parameter is present,
    or if any exception occurs, redirects to the dashboard.
    """
    url = request.META.get("HTTP_REFERER")
    if not url:
        return redirect("dashboard")

    try:
        query = requests.utils.urlparse(url).query
        params = dict(x.split("=") for x in query.split("&") if "=" in x)
        next_page = params.get("next")
        if next_page:
            return redirect(next_page)
    except Exception as e:
        # Log the exception if necessary
        pass

    return redirect("dashboard")
