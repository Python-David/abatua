from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.contrib import messages

from carts.models import CartItem
from carts.views import get_cart_id
from category.models import Category

from orders.models import OrderProduct

from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm
from accounts.config import REVIEW_SUBMITTED_MESSAGE, REVIEW_UPDATED_MESSAGE


def store(request, category_slug=None):
    if category_slug:
        categories = get_list_or_404(Category, slug=category_slug)
        products = get_list_or_404(Product, is_available=True, category__in=categories)
    else:
        products = Product.objects.filter(is_available=True).order_by("id")

    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = len(products)

    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug=None, product_slug=None):
    try:
        product = get_object_or_404(Product, slug=product_slug)
        reviews = ReviewRating.objects.filter(product=product, status=True)
        category = get_object_or_404(Category, slug=category_slug)
        in_cart = CartItem.objects.filter(
            cart__cart_id=get_cart_id(request), product=product
        ).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

    # Get product gallery
    product_gallery = ProductGallery.objects.filter(product_id=product.id)


    context = {
        "product": product,
        "category": category,
        "in_cart": in_cart,
        "order_product": order_product,
        "reviews": reviews,
        "product_gallery": product_gallery,
    }


    return render(request, "store/product_detail.html", context)


def search(request):
    products = Product.objects.none()  # Initialize with an empty queryset
    product_count = 0

    keyword = request.GET.get("keyword", "")  # Simplifies checking for 'keyword'
    if keyword:
        products = Product.objects.order_by("-date_created").filter(
            Q(product_description__icontains=keyword)
            | Q(product_name__icontains=keyword)
        )
        product_count = products.count()

    context = {
        "products": products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            # Check if the user has already reviewed this product
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
        except ReviewRating.DoesNotExist:
            # If no existing review, create a new form instance
            form = ReviewForm(request.POST)

        if form.is_valid():
            # If the form is valid, save the review
            data = form.save(commit=False)
            data.ip_address = request.META.get("REMOTE_ADDR")
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()

            if 'instance' in locals():
                messages.success(request, "Your review has been updated!")
            else:
                messages.success(request, "Your review has been submitted!")
        else:
            messages.error(request, "There was an error with your submission. Please try again.")

        return redirect(url)

    # If not POST request, redirect back
    return redirect(url)
