import os

import requests
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from PIL import Image

from carts.models import Cart, CartItem
from carts.views import get_cart_id


def send_email(user, subject, template, context):
    """
    Sends an email to the user with a custom message.
    :param user: User instance to whom the email is sent.
    :param subject: Subject of the email.
    :param template: Path to the template used for the email body.
    :param context: Context dictionary to be passed to the template.
    """

    context["user"] = user
    message = render_to_string(template, context)
    from_email = settings.DEFAULT_FROM_EMAIL
    email = EmailMessage(subject, message, from_email, to=[user.email])
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


def resize_image(image, max_size=(100, 100), quality=85, upload_to="userprofile"):
    """
    Resizes an image to the specified max_size and quality, saving it to the specified directory.

    Args:
        image: The image file to be resized.
        max_size (tuple): The maximum width and height of the resized image.
        quality (int): The quality of the resized image (1-95).
        upload_to (str): The directory to save the resized image.

    Returns:
        str: The relative path to the saved image.
    """
    try:
        img = Image.open(image)
    except UnidentifiedImageError:
        raise ValueError("The uploaded file is not a valid image.")

    # Ensure the image is not too large
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.LANCZOS)

    # Determine the file extension and format
    file_extension = os.path.splitext(image.name)[1].lower()
    if file_extension in [".jpg", ".jpeg"]:
        format = "JPEG"
    elif file_extension == ".png":
        format = "PNG"
    else:
        raise ValueError("Unsupported file extension.")

    # Ensure the directory exists
    save_directory = os.path.join(settings.MEDIA_ROOT, upload_to)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Save the resized image
    image_path = os.path.join(save_directory, image.name)
    if format == "JPEG":
        img.save(image_path, format=format, quality=quality)
    else:
        img.save(image_path, format=format)

    return os.path.join(upload_to, image.name)
