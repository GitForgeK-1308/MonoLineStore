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
