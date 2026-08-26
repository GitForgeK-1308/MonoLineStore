from django.urls import path

from .views import (
    add_to_cart,
    cart_detail,
    decrease_cart_quantity,
    increase_cart_quantity,
    remove_from_cart,
)

app_name = "cart"

urlpatterns = [
    path(
        "",
        cart_detail,
        name="cart_detail",
    ),
    path(
        "add/<slug:product_slug>/",
        add_to_cart,
        name="add_to_cart",
    ),
    path(
        "increase/<int:variant_id>/",
        increase_cart_quantity,
        name="increase_cart_quantity",
    ),
    path(
        "decrease/<int:variant_id>/",
        decrease_cart_quantity,
        name="decrease_cart_quantity",
    ),
    path(
        "remove/<int:variant_id>/",
        remove_from_cart,
        name="remove_from_cart",
    ),
]
