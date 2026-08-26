from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.exceptions import (
    CartItemUnavailableError,
    EmptyCartError,
    InsufficientStockError,
)
from orders.models import Order
from orders.services import create_order_from_cart
from products.models import (
    Category,
    Product,
    ProductVariant,
)

User = get_user_model()


class CheckoutServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="checkout@example.com",
            password="StrongPassword123!",
        )

        cls.category = Category.objects.create(
            name="Одежда",
            slug="checkout-clothes",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="checkout-hoodie",
            price=Decimal("5000.00"),
            discount=10,
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

    def get_order_data(self):
        return {
            "first_name": "Иван",
            "phone": "+79990000000",
            "email": "checkout@example.com",
            "address": "Москва",
            "comment": "Позвонить перед доставкой",
        }

    def test_checkout_creates_order(self):
        order = create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 2,
            },
            order_data=self.get_order_data(),
        )

        self.assertEqual(
            Order.objects.count(),
            1,
        )

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )

    def test_checkout_creates_order_item(self):
        order = create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 2,
            },
            order_data=self.get_order_data(),
        )

        item = order.items.get()

        self.assertEqual(
            item.variant,
            self.variant,
        )
        self.assertEqual(
            item.product_name,
            "MONO Hoodie",
        )
        self.assertEqual(
            item.quantity,
            2,
        )

    def test_checkout_uses_discounted_price(self):
        order = create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 2,
            },
            order_data=self.get_order_data(),
        )

        item = order.items.get()

        self.assertEqual(
            item.price,
            Decimal("4500.00"),
        )
        self.assertEqual(
            item.total_price,
            Decimal("9000.00"),
        )
        self.assertEqual(
            order.total_price,
            Decimal("9000.00"),
        )

    def test_checkout_decreases_stock(self):
        create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 2,
            },
            order_data=self.get_order_data(),
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )

    def test_checkout_rejects_empty_cart(self):
        with self.assertRaises(EmptyCartError):
            create_order_from_cart(
                user=self.user,
                cart={},
                order_data=self.get_order_data(),
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_checkout_rejects_insufficient_stock(self):
        with self.assertRaises(InsufficientStockError):
            create_order_from_cart(
                user=self.user,
                cart={
                    str(self.variant.pk): 6,
                },
                order_data=self.get_order_data(),
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            5,
        )

    def test_checkout_rejects_deleted_variant(self):
        variant_id = self.variant.pk

        self.variant.delete()

        with self.assertRaises(CartItemUnavailableError):
            create_order_from_cart(
                user=self.user,
                cart={
                    str(variant_id): 1,
                },
                order_data=self.get_order_data(),
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_checkout_rejects_invalid_quantity(self):
        with self.assertRaises(CartItemUnavailableError):
            create_order_from_cart(
                user=self.user,
                cart={
                    str(self.variant.pk): 0,
                },
                order_data=self.get_order_data(),
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_order_item_keeps_price_snapshot(self):
        order = create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 1,
            },
            order_data=self.get_order_data(),
        )

        item = order.items.get()

        self.product.price = Decimal("10000.00")
        self.product.discount = 0
        self.product.save()

        item.refresh_from_db()

        self.assertEqual(
            item.price,
            Decimal("4500.00"),
        )

    def test_checkout_handles_multiple_variants(self):
        second_product = Product.objects.create(
            category=self.category,
            name="MONO T-Shirt",
            slug="checkout-t-shirt",
            price=Decimal("2000.00"),
        )

        second_variant = ProductVariant.objects.create(
            product=second_product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.L,
            stock=3,
        )

        order = create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): 2,
                str(second_variant.pk): 1,
            },
            order_data=self.get_order_data(),
        )

        self.assertEqual(
            order.items.count(),
            2,
        )

        self.assertEqual(
            order.total_price,
            Decimal("11000.00"),
        )

        self.variant.refresh_from_db()
        second_variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )
        self.assertEqual(
            second_variant.stock,
            2,
        )
