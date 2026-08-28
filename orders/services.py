from decimal import Decimal

from django.db import transaction

from products.models import ProductVariant

from .exceptions import (
    CartItemUnavailableError,
    EmptyCartError,
    InsufficientStockError,
)
from .models import Order, OrderItem
from .tasks import send_order_created_email


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

    transaction.on_commit(
        lambda: send_order_created_email.delay(
            order.pk,
        )
    )

    return order


@transaction.atomic
def change_order_status(
    *,
    order_id,
    new_status,
):
    order = Order.objects.select_for_update().get(pk=order_id)

    previous_status = order.status

    order.transition_to(new_status)

    if (
        new_status == Order.Status.CANCELLED
        and previous_status != Order.Status.CANCELLED
    ):
        quantities_by_variant = {}

        order_items = order.items.exclude(
            variant_id=None,
        ).values(
            "variant_id",
            "quantity",
        )

        for item in order_items:
            variant_id = item["variant_id"]

            quantities_by_variant[variant_id] = (
                quantities_by_variant.get(
                    variant_id,
                    0,
                )
                + item["quantity"]
            )

        variants = list(
            ProductVariant.objects.select_for_update()
            .filter(
                pk__in=quantities_by_variant,
            )
            .order_by("pk")
        )

        for variant in variants:
            variant.stock += quantities_by_variant[variant.pk]

        ProductVariant.objects.bulk_update(
            variants,
            ["stock"],
        )

    return order
