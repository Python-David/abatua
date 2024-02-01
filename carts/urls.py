from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add_cart/<int:product_id>/", views.add_to_cart, name="add_cart"),
    path(
        "remove_cart/<int:product_id>/<int:cart_item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "remove_product/<int:product_id>/<int:cart_item_id>/",
        views.remove_product,
        name="remove_product",
    ),
]
