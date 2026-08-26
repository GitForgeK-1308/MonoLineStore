from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.services import CART_SESSION_KEY
from orders.models import Order
from products.models import (
    Category,
    Product,
    ProductVariant,
)

User = get_user_model()


class CheckoutFlowIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="integration@example.com",
            password="StrongPassword123!",
            first_name="Иван",
        )

        cls.category = Category.objects.create(
            name="Одежда",
            slug="integration-clothes",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="integration-mono-hoodie",
            price=Decimal("5000.00"),
            discount=10,
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

    def setUp(self):
        self.client.force_login(
            self.user,
        )

    def test_full_checkout_flow(self):
        response = self.client.post(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": self.product.slug,
                },
            ),
            {
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.M,
                "quantity": 2,
            },
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            2,
        )

        response = self.client.get(
            reverse("orders:checkout"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "first_name": "Иван",
                "phone": "+79990000000",
                "email": "integration@example.com",
                "address": "Москва",
                "comment": "",
            },
        )

        order = Order.objects.get(
            user=self.user,
        )

        self.assertRedirects(
            response,
            reverse(
                "orders:order_success",
                args=[order.pk],
            ),
        )

        self.assertEqual(
            order.total_price,
            Decimal("9000.00"),
        )

        item = order.items.get()

        self.assertEqual(
            item.product_name,
            "MONO Hoodie",
        )
        self.assertEqual(
            item.price,
            Decimal("4500.00"),
        )
        self.assertEqual(
            item.quantity,
            2,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY],
            {},
        )

        response = self.client.get(
            reverse("orders:my_orders"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            f"Заказ №{order.pk}",
        )

        response = self.client.get(
            reverse(
                "orders:order_detail",
                args=[order.pk],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "MONO Hoodie",
        )
