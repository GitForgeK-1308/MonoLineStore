from decimal import Decimal

from products.models import ProductVariant

from .exceptions import (
    InsufficientStockError,
    InvalidCartQuantityError,
)

CART_SESSION_KEY = "cart"


class SessionCart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(
            CART_SESSION_KEY,
            {},
        )

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def add(
        self,
        variant: ProductVariant,
        quantity: int = 1,
    ):
        if quantity < 1:
            raise InvalidCartQuantityError("Количество должно быть не меньше 1.")

        variant_id = str(variant.pk)

        current_quantity = self.cart.get(
            variant_id,
            0,
        )
        new_quantity = current_quantity + quantity

        if new_quantity > variant.stock:
            raise InsufficientStockError(f"Доступно только {variant.stock} шт.")

        self.cart[variant_id] = new_quantity
        self.save()

    def set_quantity(
        self,
        variant: ProductVariant,
        quantity: int,
    ):
        if quantity < 1:
            raise InvalidCartQuantityError("Количество должно быть не меньше 1.")

        if quantity > variant.stock:
            raise InsufficientStockError(f"Доступно только {variant.stock} шт.")

        self.cart[str(variant.pk)] = quantity
        self.save()

    def remove(self, variant_id: int):
        variant_id = str(variant_id)

        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def get_quantity(self, variant_id: int) -> int:
        return int(
            self.cart.get(
                str(variant_id),
                0,
            )
        )

    def __len__(self):
        return sum(int(quantity) for quantity in self.cart.values())


def get_cart_data(request):
    cart = request.session.get(
        CART_SESSION_KEY,
        {},
    )

    if not cart:
        return {
            "cart_items": [],
            "total_price": Decimal("0.00"),
            "total_quantity": 0,
        }

    variant_ids = []

    for variant_id in cart:
        try:
            variant_ids.append(int(variant_id))
        except (TypeError, ValueError):
            continue

    variants = ProductVariant.objects.select_related(
        "product",
    ).filter(pk__in=variant_ids)

    variants_by_id = {str(variant.pk): variant for variant in variants}

    cart_items = []
    total_price = Decimal("0.00")
    total_quantity = 0

    for variant_id, raw_quantity in cart.items():
        variant = variants_by_id.get(
            str(variant_id),
        )

        if variant is None:
            continue

        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue

        if quantity < 1:
            continue

        product = variant.product

        has_discount = product.discount > 0

        if has_discount:
            price = product.discounted_price
            old_price = product.price
            old_item_total = old_price * quantity
        else:
            price = product.price
            old_price = None
            old_item_total = None

        item_total = price * quantity

        cart_items.append(
            {
                "product": product,
                "variant": variant,
                "product_id": product.pk,
                "variant_id": variant.pk,
                "product_name": product.name,
                "product_slug": product.slug,
                "image": product.image,
                "color": variant.get_color_display(),
                "size": variant.size,
                "quantity": quantity,
                "price": price,
                "old_price": old_price,
                "item_total": item_total,
                "old_item_total": old_item_total,
                "discount": product.discount,
                "has_discount": has_discount,
                "in_stock": variant.in_stock,
                "available_stock": variant.stock,
                "quantity_available": (variant.stock >= quantity),
            }
        )

        total_price += item_total
        total_quantity += quantity

    return {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_quantity": total_quantity,
    }
