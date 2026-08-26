from decimal import Decimal

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from cart.exceptions import (
    InsufficientStockError,
    InvalidCartQuantityError,
)
from cart.services import (
    CART_SESSION_KEY,
    SessionCart,
)
from products.models import (
    Category,
    Product,
    ProductVariant,
)


class SessionCartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(
            name="Одежда",
            slug="cart-clothes",
        )

        product = Product.objects.create(
            category=category,
            name="MONO Hoodie",
            slug="cart-mono-hoodie",
            price=Decimal("4990.00"),
        )

        cls.variant = ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

    def setUp(self):
        request = RequestFactory().get("/")

        middleware = SessionMiddleware(
            lambda request: None,
        )
        middleware.process_request(request)
        request.session.save()

        self.request = request
        self.cart = SessionCart(request)

    def test_cart_is_empty_by_default(self):
        self.assertEqual(
            len(self.cart),
            0,
        )

    def test_add_variant_to_cart(self):
        self.cart.add(
            self.variant,
            quantity=2,
        )

        self.assertEqual(
            self.request.session[CART_SESSION_KEY],
            {
                str(self.variant.pk): 2,
            },
        )

    def test_add_same_variant_increases_quantity(self):
        self.cart.add(
            self.variant,
            quantity=2,
        )
        self.cart.add(
            self.variant,
            quantity=1,
        )

        self.assertEqual(
            self.cart.get_quantity(self.variant.pk),
            3,
        )

    def test_add_rejects_quantity_less_than_one(self):
        with self.assertRaises(
            InvalidCartQuantityError,
        ):
            self.cart.add(
                self.variant,
                quantity=0,
            )

    def test_add_rejects_quantity_greater_than_stock(self):
        with self.assertRaises(
            InsufficientStockError,
        ):
            self.cart.add(
                self.variant,
                quantity=6,
            )

    def test_total_quantity_returns_all_items_count(self):
        self.cart.add(
            self.variant,
            quantity=3,
        )

        self.assertEqual(
            len(self.cart),
            3,
        )

    def test_set_quantity(self):
        self.cart.add(
            self.variant,
            quantity=1,
        )

        self.cart.set_quantity(
            self.variant,
            quantity=4,
        )

        self.assertEqual(
            self.cart.get_quantity(self.variant.pk),
            4,
        )

    def test_set_quantity_checks_stock(self):
        with self.assertRaises(
            InsufficientStockError,
        ):
            self.cart.set_quantity(
                self.variant,
                quantity=10,
            )

    def test_remove_variant(self):
        self.cart.add(
            self.variant,
            quantity=2,
        )

        self.cart.remove(
            self.variant.pk,
        )

        self.assertEqual(
            self.cart.get_quantity(self.variant.pk),
            0,
        )

    def test_clear_cart(self):
        self.cart.add(
            self.variant,
            quantity=2,
        )

        self.cart.clear()

        self.assertEqual(
            len(self.cart),
            0,
        )
        self.assertEqual(
            self.request.session[CART_SESSION_KEY],
            {},
        )
