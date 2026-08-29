from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.templatetags.static import static
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views import defaults

from products.models import Category, Gender, Product

User = get_user_model()


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="home-clothes",
        )

        cls.gender = Gender.objects.create(
            name="Мужской",
            slug="home-male",
        )

        cls.popular_product = Product.objects.create(
            category=cls.category,
            gender=cls.gender,
            name="Popular Hoodie",
            slug="popular-hoodie",
            price=Decimal("5000.00"),
            is_popular=True,
        )

        cls.regular_product = Product.objects.create(
            category=cls.category,
            gender=cls.gender,
            name="Regular T-Shirt",
            slug="regular-t-shirt",
            price=Decimal("2000.00"),
        )

        cls.discounted_product = Product.objects.create(
            category=cls.category,
            gender=cls.gender,
            name="Discount Hoodie",
            slug="discount-hoodie",
            price=Decimal("6000.00"),
            discount=20,
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

    def test_home_page_displays_product_gender(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            self.gender.name,
        )

    def test_home_page_uses_three_queries(self):
        with self.assertNumQueries(4):
            response = self.client.get(
                reverse("core:home"),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_home_contains_guest_navigation(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            reverse("accounts:login"),
        )
        self.assertContains(
            response,
            reverse("accounts:register"),
        )
        self.assertContains(
            response,
            reverse("products:catalog"),
        )
        self.assertContains(
            response,
            reverse("cart:cart_detail"),
        )

    def test_header_displays_cart_quantity(self):
        session = self.client.session

        session["cart"] = {
            "1": 2,
        }
        session.save()

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "2",
        )