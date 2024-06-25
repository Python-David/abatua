import os

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from PIL import Image

from carts.models import Cart, CartItem
from carts.views import get_cart_id
from orders.models import Order, OrderProduct

from .config import (
    ACCOUNT_ACTIVATION_SUBJECT,
    ACCOUNT_DOES_NOT_EXIST_MESSAGE,
    ACCOUNT_VERIFICATION_FAILURE_MESSAGE,
    ACCOUNT_VERIFICATION_SUCCESS_MESSAGE,
    LOGIN_ERROR_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    PASSWORD_ERROR_MESSAGE,
    PASSWORD_RESET_SUCCESS_EMAIL,
    PASSWORD_RESET_SUCCESS_MESSAGE,
    PASSWORDS_DO_NOT_MATCH,
    PROFILE_UPDATE_SUCCESS,
    RESET_PASSWORD_ERROR_MESSAGE,
    RESET_PASSWORD_SUBJECT,
    RESET_PASSWORD_SUCCESS_MESSAGE,
)
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from .utils import merge_cart_items, redirect_to_next_page, resize_image, send_email


def register(request):
    # Pull data from form and create a new user
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )

            user.phone_number = phone_number

            user.save()

            # User activation

            send_email(
                user=user,
                subject=ACCOUNT_ACTIVATION_SUBJECT,
                template="accounts/account_verification_email.html",
                context={
                    "domain": get_current_site(request).domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )

            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method != "POST":
        return render(request, "accounts/login.html")

    email = request.POST.get("email")
    password = request.POST.get("password")
    user = auth.authenticate(email=email, password=password)

    if not user:
        messages.error(request, LOGIN_ERROR_MESSAGE)
        return redirect("login")

    # Process the cart items after successful authentication
    if merge_cart_items(request, user):
        auth.login(request, user)
        messages.success(request, LOGIN_SUCCESS_MESSAGE)
        return redirect_to_next_page(request)
    else:
        # Handle the case where cart merging fails, if necessary
        pass

    auth.login(request, user)
    messages.success(request, LOGIN_SUCCESS_MESSAGE)
    return redirect_to_next_page(request)


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, LOGOUT_SUCCESS_MESSAGE)

    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, ACCOUNT_VERIFICATION_SUCCESS_MESSAGE)
        return redirect("login")
    else:
        messages.error(request, ACCOUNT_VERIFICATION_FAILURE_MESSAGE)
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by("-created_at").filter(
        user_id=request.user.id, is_ordered=True
    )
    order_count = orders.count()
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        "order_count": order_count,
        "user_profile": user_profile,
    }
    return render(request, "accounts/dashboard.html", context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            send_email(
                user=user,
                subject=RESET_PASSWORD_SUBJECT,
                template="accounts/reset_password_email.html",
                context={
                    "domain": get_current_site(request).domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            messages.success(request, PASSWORD_RESET_SUCCESS_EMAIL)
            return redirect("login")
        else:
            messages.error(request, ACCOUNT_DOES_NOT_EXIST_MESSAGE)

            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    uid = ""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, RESET_PASSWORD_SUCCESS_MESSAGE)
        return redirect("reset_password")  # login
    else:
        messages.error(request, RESET_PASSWORD_ERROR_MESSAGE)
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, PASSWORD_RESET_SUCCESS_MESSAGE)
            return redirect("login")
        else:
            messages.error(request, PASSWORDS_DO_NOT_MATCH)
            return redirect("reset_password")

    else:
        return render(request, "accounts/reset_password.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )
    context = {"orders": orders}
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_instance = profile_form.save(commit=False)

            # Handle profile picture resizing
            if "profile_picture" in request.FILES:
                profile_picture = request.FILES["profile_picture"]
                try:
                    resized_image_path = resize_image(profile_picture)
                    profile_instance.profile_picture = resized_image_path
                except ValueError as ve:
                    messages.error(request, f"Error processing image: {ve}")
                    return redirect("edit_profile")
                except Exception as e:
                    messages.error(request, f"Unexpected error: {str(e)}")
                    return redirect("edit_profile")

            profile_instance.save()
            messages.success(request, PROFILE_UPDATE_SUCCESS)
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "user_profile": user_profile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_new_password"]

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, PASSWORD_RESET_SUCCESS_MESSAGE)

                return redirect("change_password")
            else:
                messages.error(request, PASSWORD_ERROR_MESSAGE)
                return redirect("change_password")
        else:
            messages.error(request, PASSWORDS_DO_NOT_MATCH)
            return redirect("change_password")

    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def order_detail(request, order_id):
    order_detail_object = OrderProduct.objects.filter(order__order_number=order_id)
    print(order_detail_object)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail_object:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail_object": order_detail_object,
        "order": order,
        "subtotal": subtotal,
    }
    return render(request, "accounts/order_detail.html", context)
