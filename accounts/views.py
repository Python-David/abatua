from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from accounts.forms import RegistrationForm
from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import get_cart_id

from .config import (
    ACCOUNT_ACTIVATION_SUBJECT,
    ACCOUNT_DOES_NOT_EXIST_MESSAGE,
    ACCOUNT_VERIFICATION_FAILURE_MESSAGE,
    ACCOUNT_VERIFICATION_SUCCESS_MESSAGE,
    LOGIN_ERROR_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    PASSWORD_RESET_SUCCESS_EMAIL,
    PASSWORD_RESET_SUCCESS_MESSAGE,
    PASSWORDS_DO_NOT_MATCH,
    RESET_PASSWORD_ERROR_MESSAGE,
    RESET_PASSWORD_SUBJECT,
    RESET_PASSWORD_SUCCESS_MESSAGE,
)
from .utils import send_email


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
                request=request,
                user=user,
                subject=ACCOUNT_ACTIVATION_SUBJECT,
                template="accounts/account_verification_email.html",
                redirect_url="/accounts/login/?command=verification&email=" + email,
            )

            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # User authenticated; proceed with login and cart merging
            auth.login(request, user)
            session_cart_id = get_cart_id(request)

            # Attempt to get the session cart and its items
            try:
                session_cart = Cart.objects.get(cart_id=session_cart_id)
                session_cart_items = CartItem.objects.filter(cart=session_cart)

                for session_item in session_cart_items:
                    # For each session cart item, check if the user already has a matching item
                    match_found = False
                    for user_item in CartItem.objects.filter(user=user, product=session_item.product, is_active=True):
                        if set(user_item.variations.all()) == set(session_item.variations.all()):
                            # Matching item found in the user's cart; increase quantity and delete session item
                            user_item.quantity += session_item.quantity
                            user_item.save()
                            session_item.delete()
                            match_found = True
                            break

                    if not match_found:
                        # No matching item found; assign session item to the user
                        session_item.user = user
                        session_item.cart = None
                        session_item.save()

                # If the session cart is now empty, delete it
                if not CartItem.objects.filter(cart=session_cart).exists():
                    session_cart.delete()

            except Cart.DoesNotExist:
                # No session cart to merge, proceed normally
                pass

            messages.success(request, "You are now logged in")
            return redirect("dashboard")

        else:
            # Authentication failed; return to login with error message
            messages.error(request, "Invalid login credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


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
    return render(request, "accounts/dashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            send_email(
                request=request,
                user=user,
                subject=RESET_PASSWORD_SUBJECT,
                template="accounts/reset_password_email.html",
                redirect_url="login",
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
