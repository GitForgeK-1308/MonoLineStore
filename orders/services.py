from decimal import Decimal

from django.db import transaction

from products.models import ProductVariant

from .exceptions import (
    CartItemUnavailableError,
    EmptyCartError,
    InsufficientStockError,
)
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(
    *,
    user,
    cart,
    order_data,
):
    if not cart:
        raise EmptyCartError("Корзина пуста.")

    variant_ids = []

    for variant_id in cart:
        try:
            variant_ids.append(int(variant_id))
        except (TypeError, ValueError) as error:
            raise CartItemUnavailableError(
                "В корзине найден некорректный товар."
            ) from error

    variants = list(
        ProductVariant.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=variant_ids)
        .order_by("pk")
    )

    variants_by_id = {str(variant.pk): variant for variant in variants}

    if len(variants_by_id) != len(cart):
        raise CartItemUnavailableError("Один из товаров корзины больше недоступен.")

    order_items_data = []
    total_price = Decimal("0.00")

    for variant_id, raw_quantity in cart.items():
        variant = variants_by_id.get(str(variant_id))

        if variant is None:
            raise CartItemUnavailableError("Один из товаров корзины больше недоступен.")

        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError) as error:
            raise CartItemUnavailableError("Некорректное количество товара.") from error

        if quantity < 1:
            raise CartItemUnavailableError("Количество товара должно быть не меньше 1.")

        if quantity > variant.stock:
            raise InsufficientStockError(
                f"Для товара «{variant.product.name}» "
                f"доступно только {variant.stock} шт."
            )

        product = variant.product

        if product.discount:
            price = product.discounted_price
        else:
            price = product.price

        item_total = price * quantity
        total_price += item_total

        order_items_data.append(
            {
                "variant": variant,
                "product_name": product.name,
                "product_slug": product.slug,
                "color": variant.get_color_display(),
                "size": variant.get_size_display(),
                "price": price,
                "quantity": quantity,
            }
        )

    order = Order.objects.create(
        user=user,
        first_name=order_data["first_name"],
        phone=order_data["phone"],
        email=order_data["email"],
        address=order_data["address"],
        comment=order_data.get(
            "comment",
            "",
        ),
        total_price=total_price,
    )

    order_items = []

    for item_data in order_items_data:
        variant = item_data["variant"]
        quantity = item_data["quantity"]

        order_items.append(
            OrderItem(
                order=order,
                variant=variant,
                product_name=item_data["product_name"],
                product_slug=item_data["product_slug"],
                color=item_data["color"],
                size=item_data["size"],
                price=item_data["price"],
                quantity=quantity,
            )
        )

        variant.stock -= quantity
        variant.save(
            update_fields=["stock"],
        )

    OrderItem.objects.bulk_create(order_items)

    return order
