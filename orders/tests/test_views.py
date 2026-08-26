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


class CheckoutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="checkout-view@example.com",
            password="StrongPassword123!",
            first_name="Иван",
        )

        cls.category = Category.objects.create(
            name="Одежда",
            slug="checkout-view-clothes",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="checkout-view-hoodie",
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
        self.client.force_login(self.user)

    def add_product_to_cart(self, quantity=1):
        session = self.client.session

        session[CART_SESSION_KEY] = {
            str(self.variant.pk): quantity,
        }

        session.save()

    def get_order_data(self):
        return {
            "first_name": "Иван",
            "phone": "+79990000000",
            "email": "checkout-view@example.com",
            "address": "Москва",
            "comment": "",
        }

    def test_checkout_requires_authentication(self):
        self.client.logout()

        response = self.client.get(
            reverse("orders:checkout"),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_empty_cart_redirects_to_cart(self):
        response = self.client.get(
            reverse("orders:checkout"),
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

    def test_checkout_page_is_available(self):
        self.add_product_to_cart()

        response = self.client.get(
            reverse("orders:checkout"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "orders/checkout.html",
        )

    def test_checkout_prefills_user_data(self):
        self.add_product_to_cart()

        response = self.client.get(
            reverse("orders:checkout"),
        )

        form = response.context["form"]

        self.assertEqual(
            form.initial["first_name"],
            "Иван",
        )
        self.assertEqual(
            form.initial["email"],
            self.user.email,
        )

    def test_checkout_creates_order(self):
        self.add_product_to_cart(
            quantity=2,
        )

        response = self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        order = Order.objects.get()

        self.assertRedirects(
            response,
            reverse(
                "orders:order_success",
                args=[order.pk],
            ),
        )

        self.assertEqual(
            order.user,
            self.user,
        )
        self.assertEqual(
            order.total_price,
            Decimal("9000.00"),
        )

    def test_successful_checkout_clears_cart(self):
        self.add_product_to_cart()

        self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY],
            {},
        )

    def test_successful_checkout_decreases_stock(self):
        self.add_product_to_cart(
            quantity=2,
        )

        self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            3,
        )

    def test_invalid_form_does_not_create_order(self):
        self.add_product_to_cart()

        data = self.get_order_data()
        data["email"] = "invalid-email"

        response = self.client.post(
            reverse("orders:checkout"),
            data,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.assertIn(
            CART_SESSION_KEY,
            self.client.session,
        )

    def test_insufficient_stock_does_not_create_order(self):
        self.add_product_to_cart(
            quantity=6,
        )

        response = self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.assertNotEqual(
            self.client.session[CART_SESSION_KEY],
            {},
        )

    def test_order_success_is_available_to_owner(self):
        self.add_product_to_cart()

        self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        order = Order.objects.get()

        response = self.client.get(
            reverse(
                "orders:order_success",
                args=[order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            f"№{order.pk}",
        )

    def test_order_success_is_not_available_to_another_user(self):
        self.add_product_to_cart()

        self.client.post(
            reverse("orders:checkout"),
            self.get_order_data(),
        )

        order = Order.objects.get()

        other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(other_user)

        response = self.client.get(
            reverse(
                "orders:order_success",
                args=[order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class OrderHistoryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="orders-history@example.com",
            password="StrongPassword123!",
        )

        cls.other_user = User.objects.create_user(
            email="other-history@example.com",
            password="StrongPassword123!",
        )

        cls.order = Order.objects.create(
            user=cls.user,
            first_name="Иван",
            phone="+79990000000",
            email="orders-history@example.com",
            address="Москва",
            total_price=Decimal("5000.00"),
        )

        cls.other_order = Order.objects.create(
            user=cls.other_user,
            first_name="Пётр",
            phone="+79991111111",
            email="other-history@example.com",
            address="Омск",
            total_price=Decimal("7000.00"),
        )

    def setUp(self):
        self.client.force_login(
            self.user,
        )

    def test_order_list_requires_authentication(self):
        self.client.logout()

        response = self.client.get(
            reverse("orders:my_orders"),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_order_list_is_available(self):
        response = self.client.get(
            reverse("orders:my_orders"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "orders/my_orders.html",
        )

    def test_order_list_contains_only_current_user_orders(self):
        response = self.client.get(
            reverse("orders:my_orders"),
        )

        orders = list(
            response.context["orders"],
        )

        self.assertIn(
            self.order,
            orders,
        )
        self.assertNotIn(
            self.other_order,
            orders,
        )

    def test_order_detail_requires_authentication(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                "orders:order_detail",
                args=[self.order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_order_detail_is_available_to_owner(self):
        response = self.client.get(
            reverse(
                "orders:order_detail",
                args=[self.order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "orders/order_detail.html",
        )
        self.assertEqual(
            response.context["order"],
            self.order,
        )

    def test_order_detail_is_not_available_to_another_user(self):
        response = self.client.get(
            reverse(
                "orders:order_detail",
                args=[self.other_order.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_unknown_order_returns_404(self):
        response = self.client.get(
            reverse(
                "orders:order_detail",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_order_list_is_paginated_by_ten(self):
        for number in range(10):
            Order.objects.create(
                user=self.user,
                first_name="Иван",
                phone="+79990000000",
                email="orders-history@example.com",
                address=f"Адрес {number}",
                total_price=Decimal("1000.00"),
            )

        response = self.client.get(
            reverse("orders:my_orders"),
        )

        self.assertTrue(
            response.context["is_paginated"],
        )
        self.assertEqual(
            response.context["paginator"].per_page,
            10,
        )
