import datetime
import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from accounts.config import ORDER_CONFIRMATION_SUBJECT
from accounts.utils import send_email
from carts.models import CartItem
from store.models import Product

from .forms import Order, OrderForm
from .models import OrderProduct, Payment


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )

    # Store transaction details in the Payment Model

    payment = Payment(
        user=request.user,
        payment_id=body["transactionID"],
        payment_method=body["paymentMethod"],
        amount_paid=order.order_total,
        status=body["status"],
    )

    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move ordered items into OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)

    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = cart_item.product_id
        order_product.quantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.ordered = True

        order_product.save()

        cart_item = CartItem.objects.get(id=cart_item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # Reduce quantity of products in stock
        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order confirmation email to customer

    send_email(
        user=request.user,
        subject=ORDER_CONFIRMATION_SUBJECT,
        template="orders/order_received_email.html",
        context={"order": order},
    )

    # Send order number and transaction id back to sendData method in frontend via JSON response

    data = {
        "order_number": order.order_number,
        "transaction_id": payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If user cart is empty, redirect back to shop

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect("store")

    total_tax = 0

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
        tax = cart_item.get_tax(3)
        total_tax += tax

    grand_total = total + total_tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing info inside Order table
            data = Order()

            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = total_tax
            data.ip = request.META.get("REMOTE_ADDR")

            data.save()

            # Generate order number

            year = int(datetime.date.today().strftime("%Y"))
            day = int(datetime.date.today().strftime("%d"))
            month = int(datetime.date.today().strftime("%m"))
            date = datetime.date(year, month, day)
            curent_date = date.strftime("%Y%m%d")

            order_number = curent_date + str(data.id)

            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )

            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "grand_total": grand_total,
                "total_tax": total_tax,
                "paypal_client_id": settings.PAYPAL_CLIENT_ID,
                "payment_method": "PayPal",  # TODO remember to change this for when we offer multiple payment method support
            }

            return render(request, "orders/payments.html", context)

    else:
        return redirect("checkout")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transaction_id)

        context = {
            "order": order,
            "order_products": order_products,
            "order_number": order.order_number,
            "transaction_id": payment.payment_id,
            "subtotal": subtotal,
            "payment": payment,
        }
        return render(request, "orders/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
