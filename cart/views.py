from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.forms import AddToCartForm
from products.models import Product, ProductVariant

from .exceptions import InsufficientStockError
from .services import SessionCart, get_cart_data


def cart_detail(request):
    cart_data = get_cart_data(request)

    return render(
        request,
        "cart/cart_detail.html",
        cart_data,
    )


@require_POST
def add_to_cart(request, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
    )

    form = AddToCartForm(
        request.POST,
        product=product,
    )

    if not form.is_valid():
        messages.error(
            request,
            "Не удалось добавить товар. Проверьте выбранный вариант.",
        )

        return redirect(
            "products:product_detail",
            product_slug=product.slug,
        )

    variant = form.cleaned_data["variant"]
    quantity = form.cleaned_data["quantity"]

    cart = SessionCart(request)

    try:
        cart.add(
            variant,
            quantity=quantity,
        )
    except InsufficientStockError as error:
        messages.error(
            request,
            str(error),
        )

        return redirect(
            "products:product_detail",
            product_slug=product.slug,
        )

    messages.success(
        request,
        "Товар добавлен в корзину.",
    )

    return redirect(
        "cart:cart_detail",
    )


@require_POST
def increase_cart_quantity(request, variant_id):
    cart = SessionCart(request)

    current_quantity = cart.get_quantity(
        variant_id,
    )

    if current_quantity == 0:
        messages.error(
            request,
            "Товар не найден в корзине.",
        )
        return redirect("cart:cart_detail")

    variant = get_object_or_404(
        ProductVariant,
        pk=variant_id,
    )

    try:
        cart.set_quantity(
            variant,
            quantity=current_quantity + 1,
        )
    except InsufficientStockError as error:
        messages.error(
            request,
            str(error),
        )

    return redirect("cart:cart_detail")


@require_POST
def decrease_cart_quantity(request, variant_id):
    cart = SessionCart(request)

    current_quantity = cart.get_quantity(
        variant_id,
    )

    if current_quantity == 0:
        messages.error(
            request,
            "Товар не найден в корзине.",
        )
        return redirect("cart:cart_detail")

    if current_quantity == 1:
        return redirect("cart:cart_detail")

    variant = get_object_or_404(
        ProductVariant,
        pk=variant_id,
    )

    cart.set_quantity(
        variant,
        quantity=current_quantity - 1,
    )

    return redirect("cart:cart_detail")


@require_POST
def remove_from_cart(request, variant_id):
    cart = SessionCart(request)

    if cart.get_quantity(variant_id) == 0:
        messages.error(
            request,
            "Товар не найден в корзине.",
        )
        return redirect("cart:cart_detail")

    cart.remove(
        variant_id,
    )

    messages.success(
        request,
        "Товар удалён из корзины.",
    )

    return redirect("cart:cart_detail")
