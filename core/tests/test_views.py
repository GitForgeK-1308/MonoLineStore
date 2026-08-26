from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="home-clothes",
        )

        cls.popular_product = Product.objects.create(
            category=cls.category,
            name="Popular Hoodie",
            slug="popular-hoodie",
            price=Decimal("5000.00"),
            is_popular=True,
        )

        cls.regular_product = Product.objects.create(
            category=cls.category,
            name="Regular T-Shirt",
            slug="regular-t-shirt",
            price=Decimal("2000.00"),
        )

    def test_home_page_is_available(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_home_page_uses_correct_template(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertTemplateUsed(
            response,
            "core/home.html",
        )

    def test_home_contains_popular_products(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertIn(
            self.popular_product,
            response.context["popular_products"],
        )

    def test_regular_product_is_not_in_popular_products(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertNotIn(
            self.regular_product,
            response.context["popular_products"],
        )

    def test_home_contains_new_products(self):
        response = self.client.get(
            reverse("core:home"),
        )

        new_products = response.context["new_products"]

        self.assertIn(
            self.popular_product,
            new_products,
        )
        self.assertIn(
            self.regular_product,
            new_products,
        )

    def test_home_page_uses_two_product_queries(self):
        with self.assertNumQueries(2):
            response = self.client.get(
                reverse("core:home"),
            )

        self.assertEqual(
            response.status_code,
            200,
        )
