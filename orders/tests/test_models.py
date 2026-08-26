from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from orders.models import Order, OrderItem
from products.models import (
    Category,
    Product,
    ProductVariant,
)

User = get_user_model()


class OrderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="customer@example.com",
            password="StrongPassword123!",
        )

    def test_order_is_created_with_new_status(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
        )

        self.assertEqual(
            order.status,
            Order.Status.NEW,
        )

    def test_order_string_representation(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
        )

        self.assertEqual(
            str(order),
            f"Заказ №{order.pk}",
        )

    def test_order_can_exist_without_user(self):
        order = Order.objects.create(
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
        )

        self.assertIsNone(order.user)

    def test_deleting_user_does_not_delete_order(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
        )

        self.user.delete()

        order.refresh_from_db()

        self.assertIsNone(order.user)

    def test_order_total_price_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Order.objects.create(
                    first_name="Иван",
                    phone="+79990000000",
                    email="customer@example.com",
                    address="Москва",
                    total_price=Decimal("-0.01"),
                )

    def test_order_total_price_can_be_zero(self):
        order = Order.objects.create(
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("0.00"),
        )

        self.assertEqual(
            order.total_price,
            Decimal("0.00"),
        )


class OrderItemModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="orders-clothes",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="orders-mono-hoodie",
            price=Decimal("5000.00"),
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        cls.order = Order.objects.create(
            first_name="Иван",
            phone="+79990000000",
            email="customer@example.com",
            address="Москва",
            total_price=Decimal("9000.00"),
        )

    def create_order_item(self, **kwargs):
        data = {
            "order": self.order,
            "variant": self.variant,
            "product_name": self.product.name,
            "product_slug": self.product.slug,
            "color": self.variant.get_color_display(),
            "size": self.variant.get_size_display(),
            "price": Decimal("4500.00"),
            "quantity": 2,
        }

        data.update(kwargs)

        return OrderItem.objects.create(**data)

    def test_order_item_is_created(self):
        item = self.create_order_item()

        self.assertEqual(
            item.order,
            self.order,
        )
        self.assertEqual(
            item.variant,
            self.variant,
        )

    def test_order_item_total_price_is_calculated(self):
        item = self.create_order_item()

        self.assertEqual(
            item.total_price,
            Decimal("9000.00"),
        )

    def test_order_item_string_representation(self):
        item = self.create_order_item()

        self.assertEqual(
            str(item),
            self.product.name,
        )

    def test_order_item_snapshot_does_not_change_with_product(self):
        item = self.create_order_item()

        self.product.name = "Новое название"
        self.product.price = Decimal("9999.00")
        self.product.save()

        item.refresh_from_db()

        self.assertEqual(
            item.product_name,
            "MONO Hoodie",
        )
        self.assertEqual(
            item.price,
            Decimal("4500.00"),
        )

    def test_deleting_variant_keeps_order_item(self):
        item = self.create_order_item()

        self.variant.delete()

        item.refresh_from_db()

        self.assertIsNone(item.variant)
        self.assertEqual(
            item.product_name,
            "MONO Hoodie",
        )

    def test_deleting_order_deletes_items(self):
        item = self.create_order_item()
        item_id = item.pk

        self.order.delete()

        self.assertFalse(
            OrderItem.objects.filter(
                pk=item_id,
            ).exists()
        )

    def test_order_item_quantity_cannot_be_zero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_order_item(
                    quantity=0,
                )

    def test_order_item_price_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_order_item(
                    price=Decimal("-0.01"),
                )

    def test_order_item_price_can_be_zero(self):
        item = self.create_order_item(
            price=Decimal("0.00"),
        )

        self.assertEqual(
            item.price,
            Decimal("0.00"),
        )
