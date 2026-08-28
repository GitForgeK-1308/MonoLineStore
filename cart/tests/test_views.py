from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from cart.services import CART_SESSION_KEY
from products.models import (
    Category,
    Product,
    ProductVariant,
)


class CartViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(
            name="Одежда",
            slug="cart-views-clothes",
        )

        cls.product = Product.objects.create(
            category=category,
            name="MONO Hoodie",
            slug="cart-views-hoodie",
            price=Decimal("5000.00"),
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

    def test_cart_detail_is_available(self):
        response = self.client.get(
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "cart/cart_detail.html",
        )

    def test_empty_cart_is_displayed(self):
        response = self.client.get(
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            response.context["cart_items"],
            [],
        )
        self.assertEqual(
            response.context["total_quantity"],
            0,
        )

    def test_add_product_to_cart(self):
        response = self.client.post(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": self.product.slug,
                },
            ),
            {
                "color": self.variant.color,
                "size": self.variant.size,
                "quantity": 2,
            },
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        session = self.client.session

        self.assertEqual(
            session[CART_SESSION_KEY],
            {
                str(self.variant.pk): 2,
            },
        )

    def test_add_same_product_increases_quantity(self):
        url = reverse(
            "cart:add_to_cart",
            kwargs={
                "product_slug": self.product.slug,
            },
        )

        data = {
            "color": self.variant.color,
            "size": self.variant.size,
            "quantity": 1,
        }

        self.client.post(
            url,
            data,
        )
        self.client.post(
            url,
            data,
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            2,
        )

    def test_add_to_cart_does_not_accept_get(self):
        response = self.client.get(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_invalid_quantity_is_not_added(self):
        response = self.client.post(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": self.product.slug,
                },
            ),
            {
                "color": self.variant.color,
                "size": self.variant.size,
                "quantity": 10,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            ),
        )

        self.assertNotIn(
            CART_SESSION_KEY,
            self.client.session,
        )

    def test_unknown_product_returns_404(self):
        response = self.client.post(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": "unknown-product",
                },
            ),
            {
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.M,
                "quantity": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_cart_detail_contains_added_product(self):
        self.client.post(
            reverse(
                "cart:add_to_cart",
                kwargs={
                    "product_slug": self.product.slug,
                },
            ),
            {
                "color": self.variant.color,
                "size": self.variant.size,
                "quantity": 2,
            },
        )

        response = self.client.get(
            reverse("cart:cart_detail"),
        )

        self.assertContains(
            response,
            self.product.name,
        )

        self.assertEqual(
            response.context["total_quantity"],
            2,
        )

        self.assertEqual(
            response.context["total_price"],
            Decimal("10000.00"),
        )

    def add_variant_to_session_cart(
        self,
        quantity=1,
    ):
        session = self.client.session

        session[CART_SESSION_KEY] = {
            str(self.variant.pk): quantity,
        }

        session.save()

    def test_increase_cart_quantity(self):
        self.add_variant_to_session_cart(
            quantity=2,
        )

        response = self.client.post(
            reverse(
                "cart:increase_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            3,
        )

    def test_increase_cart_quantity_checks_stock(self):
        self.add_variant_to_session_cart(
            quantity=5,
        )

        self.client.post(
            reverse(
                "cart:increase_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            5,
        )

    def test_decrease_cart_quantity(self):
        self.add_variant_to_session_cart(
            quantity=3,
        )

        response = self.client.post(
            reverse(
                "cart:decrease_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            2,
        )

    def test_decrease_does_not_go_below_one(self):
        self.add_variant_to_session_cart(
            quantity=1,
        )

        self.client.post(
            reverse(
                "cart:decrease_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.variant.pk)],
            1,
        )

    def test_remove_from_cart(self):
        self.add_variant_to_session_cart(
            quantity=2,
        )

        response = self.client.post(
            reverse(
                "cart:remove_from_cart",
                args=[self.variant.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        self.assertNotIn(
            str(self.variant.pk),
            self.client.session[CART_SESSION_KEY],
        )

    def test_increase_does_not_accept_get(self):
        self.add_variant_to_session_cart()

        response = self.client.get(
            reverse(
                "cart:increase_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_decrease_does_not_accept_get(self):
        self.add_variant_to_session_cart()

        response = self.client.get(
            reverse(
                "cart:decrease_cart_quantity",
                args=[self.variant.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_remove_does_not_accept_get(self):
        self.add_variant_to_session_cart()

        response = self.client.get(
            reverse(
                "cart:remove_from_cart",
                args=[self.variant.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_cart_detail_includes_stylesheet(self):
        response = self.client.get(
            reverse("cart:cart_detail"),
        )

        self.assertContains(
            response,
            "/static/cart/css/cart.css",
        )

    def test_cart_with_items_contains_checkout_link(self):
        self.add_variant_to_session_cart(
            quantity=1,
        )

        response = self.client.get(
            reverse("cart:cart_detail"),
        )

        self.assertContains(
            response,
            reverse("orders:checkout"),
        )
