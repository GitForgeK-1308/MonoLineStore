from decimal import Decimal

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from cart.services import (
    CART_SESSION_KEY,
    get_cart_data,
)
from products.models import (
    Category,
    Product,
    ProductVariant,
)


class CartDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(
            name="Одежда",
            slug="cart-data-clothes",
        )

        cls.product = Product.objects.create(
            category=category,
            name="MONO Hoodie",
            slug="cart-data-hoodie",
            price=Decimal("5000.00"),
            discount=10,
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        cls.regular_product = Product.objects.create(
            category=category,
            name="MONO T-Shirt",
            slug="cart-data-t-shirt",
            price=Decimal("2000.00"),
        )

        cls.regular_variant = ProductVariant.objects.create(
            product=cls.regular_product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.L,
            stock=3,
        )

    def setUp(self):
        self.request = RequestFactory().get("/")

        middleware = SessionMiddleware(
            lambda request: None,
        )
        middleware.process_request(self.request)
        self.request.session.save()

    def test_empty_cart_returns_zero_totals(self):
        data = get_cart_data(self.request)

        self.assertEqual(
            data["cart_items"],
            [],
        )
        self.assertEqual(
            data["total_price"],
            Decimal("0.00"),
        )
        self.assertEqual(
            data["total_quantity"],
            0,
        )

    def test_cart_contains_product_data(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.variant.pk): 2,
        }

        data = get_cart_data(self.request)

        item = data["cart_items"][0]

        self.assertEqual(
            item["product"],
            self.product,
        )
        self.assertEqual(
            item["variant"],
            self.variant,
        )
        self.assertEqual(
            item["quantity"],
            2,
        )

    def test_discounted_price_is_used(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.variant.pk): 2,
        }

        data = get_cart_data(self.request)

        item = data["cart_items"][0]

        self.assertEqual(
            item["price"],
            Decimal("4500.00"),
        )
        self.assertEqual(
            item["item_total"],
            Decimal("9000.00"),
        )
        self.assertEqual(
            item["old_price"],
            Decimal("5000.00"),
        )

    def test_regular_price_is_used_without_discount(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.regular_variant.pk): 2,
        }

        data = get_cart_data(self.request)

        item = data["cart_items"][0]

        self.assertEqual(
            item["price"],
            Decimal("2000.00"),
        )
        self.assertIsNone(
            item["old_price"],
        )
        self.assertFalse(
            item["has_discount"],
        )

    def test_total_price_is_calculated(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.variant.pk): 2,
            str(self.regular_variant.pk): 1,
        }

        data = get_cart_data(self.request)

        self.assertEqual(
            data["total_price"],
            Decimal("11000.00"),
        )
        self.assertEqual(
            data["total_quantity"],
            3,
        )

    def test_unavailable_quantity_is_detected(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.variant.pk): 10,
        }

        data = get_cart_data(self.request)

        item = data["cart_items"][0]

        self.assertFalse(
            item["quantity_available"],
        )
        self.assertEqual(
            item["available_stock"],
            5,
        )

    def test_deleted_variant_is_ignored(self):
        variant_id = self.regular_variant.pk

        self.request.session[CART_SESSION_KEY] = {
            str(variant_id): 1,
        }

        self.regular_variant.delete()

        data = get_cart_data(self.request)

        self.assertEqual(
            data["cart_items"],
            [],
        )

    def test_cart_products_are_loaded_in_one_query(self):
        self.request.session[CART_SESSION_KEY] = {
            str(self.variant.pk): 2,
            str(self.regular_variant.pk): 1,
        }

        with self.assertNumQueries(1):
            data = get_cart_data(self.request)

            list(data["cart_items"])
