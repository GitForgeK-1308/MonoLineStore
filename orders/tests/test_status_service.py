from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order
from orders.services import (
    change_order_status,
    create_order_from_cart,
)
from products.models import (
    Category,
    Product,
    ProductVariant,
)

User = get_user_model()


class OrderStatusServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="status-service@example.com",
            password="StrongPassword123!",
        )

        cls.category = Category.objects.create(
            name="Одежда",
            slug="status-service-clothes",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="status-service-hoodie",
            price=Decimal("5000.00"),
        )

    def setUp(self):
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

    def get_order_data(self):
        return {
            "first_name": "Иван",
            "phone": "+79990000000",
            "email": "status-service@example.com",
            "address": "Москва",
            "comment": "",
        }

    def create_order(self, quantity=2):
        return create_order_from_cart(
            user=self.user,
            cart={
                str(self.variant.pk): quantity,
            },
            order_data=self.get_order_data(),
        )

    def test_change_status_to_processing(self):
        order = self.create_order()

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.PROCESSING,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PROCESSING,
        )

    def test_processing_does_not_restore_stock(self):
        order = self.create_order(
            quantity=2,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.PROCESSING,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )

    def test_cancelling_new_order_restores_stock(self):
        order = self.create_order(
            quantity=2,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.CANCELLED,
        )

        self.variant.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED,
        )
        self.assertEqual(
            self.variant.stock,
            5,
        )

    def test_cancelling_processing_order_restores_stock(self):
        order = self.create_order(
            quantity=2,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.PROCESSING,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.CANCELLED,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            5,
        )

    def test_cancelled_order_does_not_restore_stock_twice(self):
        order = self.create_order(
            quantity=2,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.CANCELLED,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            5,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.CANCELLED,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            5,
        )

    def test_invalid_transition_does_not_restore_stock(self):
        order = self.create_order(
            quantity=2,
        )

        with self.assertRaises(ValidationError):
            change_order_status(
                order_id=order.pk,
                new_status=Order.Status.COMPLETED,
            )

        order.refresh_from_db()
        self.variant.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )
        self.assertEqual(
            self.variant.stock,
            3,
        )

    def test_completed_order_cannot_be_cancelled(self):
        order = self.create_order(
            quantity=2,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.PROCESSING,
        )

        change_order_status(
            order_id=order.pk,
            new_status=Order.Status.COMPLETED,
        )

        with self.assertRaises(ValidationError):
            change_order_status(
                order_id=order.pk,
                new_status=Order.Status.CANCELLED,
            )

        order.refresh_from_db()
        self.variant.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.COMPLETED,
        )
        self.assertEqual(
            self.variant.stock,
            3,
        )
