from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.admin import OrderAdmin, OrderItemAdmin
from orders.models import Order, OrderItem
from products.models import (
    Category,
    Product,
    ProductVariant,
)

User = get_user_model()


class OrderAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            email="admin-orders@example.com",
            password="StrongAdminPassword123!",
        )

        cls.customer = User.objects.create_user(
            email="customer-orders@example.com",
            password="StrongPassword123!",
        )

        category = Category.objects.create(
            name="Одежда",
            slug="orders-admin-clothes",
        )

        product = Product.objects.create(
            category=category,
            name="MONO Hoodie",
            slug="orders-admin-hoodie",
            price=Decimal("5000.00"),
        )

        variant = ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        cls.order = Order.objects.create(
            user=cls.customer,
            first_name="Иван",
            phone="+79990000000",
            email="customer-orders@example.com",
            address="Москва",
            total_price=Decimal("9000.00"),
        )

        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            variant=variant,
            product_name=product.name,
            product_slug=product.slug,
            color=variant.get_color_display(),
            size=variant.get_size_display(),
            price=Decimal("4500.00"),
            quantity=2,
        )

    def setUp(self):
        self.client.force_login(
            self.admin_user,
        )

    def test_order_changelist_is_available(self):
        response = self.client.get(
            reverse("admin:orders_order_changelist"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_order_is_displayed_in_admin(self):
        response = self.client.get(
            reverse("admin:orders_order_changelist"),
        )

        self.assertContains(
            response,
            self.order.email,
        )
        self.assertContains(
            response,
            self.order.phone,
        )

    def test_order_change_page_contains_order_item(self):
        response = self.client.get(
            reverse(
                "admin:orders_order_change",
                args=[self.order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            self.order_item.product_name,
        )

    def test_order_status_is_editable(self):
        model_admin = admin.site._registry[Order]

        self.assertNotIn(
            "status",
            model_admin.readonly_fields,
        )

    def test_order_customer_data_is_read_only(self):
        model_admin = admin.site._registry[Order]

        self.assertIn(
            "email",
            model_admin.readonly_fields,
        )
        self.assertIn(
            "total_price",
            model_admin.readonly_fields,
        )

    def test_order_item_cannot_be_created_from_admin(self):
        model_admin = admin.site._registry[OrderItem]

        self.assertFalse(
            model_admin.has_add_permission(
                None,
            )
        )

    def test_order_item_cannot_be_deleted_from_admin(self):
        model_admin = admin.site._registry[OrderItem]

        self.assertFalse(
            model_admin.has_delete_permission(
                None,
                self.order_item,
            )
        )

    def test_correct_admin_classes_are_registered(self):
        self.assertIsInstance(
            admin.site._registry[Order],
            OrderAdmin,
        )
        self.assertIsInstance(
            admin.site._registry[OrderItem],
            OrderItemAdmin,
        )
