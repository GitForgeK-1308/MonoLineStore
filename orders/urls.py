from django.urls import path

from .views import (
    OrderDetailView,
    OrderListView,
    checkout,
    order_success,
)

app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        checkout,
        name="checkout",
    ),
    path(
        "success/<int:order_id>/",
        order_success,
        name="order_success",
    ),
    path(
        "my/",
        OrderListView.as_view(),
        name="my_orders",
    ),
    path(
        "my/<int:order_id>/",
        OrderDetailView.as_view(),
        name="order_detail",
    ),
]
