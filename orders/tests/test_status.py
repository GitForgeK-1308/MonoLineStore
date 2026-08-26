from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order


class OrderStatusTests(TestCase):
    def create_order(self, status=Order.Status.NEW):
        return Order.objects.create(
            first_name="Иван",
            phone="+79990000000",
            email="status@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
            status=status,
        )

    def test_new_order_can_move_to_processing(self):
        order = self.create_order()

        order.transition_to(Order.Status.PROCESSING)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PROCESSING,
        )

    def test_new_order_can_be_cancelled(self):
        order = self.create_order()

        order.transition_to(Order.Status.CANCELLED)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED,
        )

    def test_new_order_cannot_move_directly_to_completed(self):
        order = self.create_order()

        with self.assertRaises(ValidationError):
            order.transition_to(Order.Status.COMPLETED)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )

    def test_processing_order_can_move_to_completed(self):
        order = self.create_order(
            status=Order.Status.PROCESSING,
        )

        order.transition_to(Order.Status.COMPLETED)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.COMPLETED,
        )

    def test_processing_order_can_be_cancelled(self):
        order = self.create_order(
            status=Order.Status.PROCESSING,
        )

        order.transition_to(Order.Status.CANCELLED)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED,
        )

    def test_completed_order_cannot_return_to_processing(self):
        order = self.create_order(
            status=Order.Status.COMPLETED,
        )

        with self.assertRaises(ValidationError):
            order.transition_to(Order.Status.PROCESSING)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.COMPLETED,
        )

    def test_cancelled_order_cannot_return_to_new(self):
        order = self.create_order(
            status=Order.Status.CANCELLED,
        )

        with self.assertRaises(ValidationError):
            order.transition_to(Order.Status.NEW)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED,
        )

    def test_same_status_is_allowed(self):
        order = self.create_order()

        order.transition_to(Order.Status.NEW)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )

    def test_unknown_status_is_rejected(self):
        order = self.create_order()

        with self.assertRaises(ValidationError):
            order.transition_to("unknown")

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )
