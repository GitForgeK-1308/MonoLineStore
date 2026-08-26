from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cart.services import (
    CART_SESSION_KEY,
    SessionCart,
    get_cart_data,
)

from .exceptions import CheckoutError
from .forms import OrderCreateForm
from .models import Order
from .services import create_order_from_cart


@login_required
def checkout(request):
    cart_data = get_cart_data(request)

    if not cart_data["cart_items"]:
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = OrderCreateForm(
            request.POST,
        )

        if form.is_valid():
            try:
                order = create_order_from_cart(
                    user=request.user,
                    cart=request.session.get(
                        CART_SESSION_KEY,
                        {},
                    ),
                    order_data=form.cleaned_data,
                )
            except CheckoutError as error:
                messages.error(
                    request,
                    str(error),
                )
                return redirect("cart:cart_detail")

            SessionCart(request).clear()

            return redirect(
                "orders:order_success",
                order_id=order.pk,
            )
    else:
        form = OrderCreateForm(
            initial={
                "first_name": request.user.first_name,
                "email": request.user.email,
            }
        )

    context = {
        "form": form,
        "cart_items": cart_data["cart_items"],
        "total_price": cart_data["total_price"],
        "total_quantity": cart_data["total_quantity"],
    }

    return render(
        request,
        "orders/checkout.html",
        context,
    )


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
        },
    )
