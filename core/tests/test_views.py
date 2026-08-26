from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

User = get_user_model()


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

        cls.discounted_product = Product.objects.create(
            category=cls.category,
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
            "10": 2,
            "20": 1,
        }

        session.save()

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "Корзина (3)",
        )

    def test_home_contains_authenticated_navigation(self):
        user = User.objects.create_user(
            email="header-user@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            user,
        )

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            reverse("accounts:profile"),
        )
        self.assertContains(
            response,
            reverse("orders:my_orders"),
        )

        self.assertNotContains(
            response,
            reverse("accounts:login"),
        )
        self.assertNotContains(
            response,
            reverse("accounts:register"),
        )

    def test_home_contains_categories(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertIn(
            self.category,
            response.context["categories"],
        )

    def test_home_contains_category_catalog_link(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            reverse(
                "products:catalog",
                kwargs={
                    "category_slug": self.category.slug,
                },
            ),
        )

    def test_home_contains_discounted_products(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertIn(
            self.discounted_product,
            response.context["discount_products"],
        )

    def test_home_discount_products_exclude_products_without_discount(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertNotIn(
            self.regular_product,
            response.context["discount_products"],
        )

    def test_home_includes_base_stylesheet(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "/static/core/css/base.css",
        )

    def test_home_includes_home_stylesheet(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "/static/core/css/home.css",
        )

    def test_home_includes_product_card_stylesheet(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "/static/products/css/product_card.css",
        )

    def test_home_popular_link_uses_catalog_filter(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            f"{reverse('products:catalog')}?is_popular=1",
        )

    def test_home_discount_link_uses_catalog_filter(self):
        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            f"{reverse('products:catalog')}?discount=1",
        )
