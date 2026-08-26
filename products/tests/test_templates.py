from decimal import Decimal

from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class ProductCardTemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="template-clothes",
        )

        cls.regular_product = Product.objects.create(
            category=cls.category,
            name="MONO T-Shirt",
            slug="template-mono-t-shirt",
            price=Decimal("2000.00"),
        )

        cls.discounted_product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie",
            slug="template-mono-hoodie",
            price=Decimal("5000.00"),
            discount=10,
        )

    def render_card(self, product):
        return render_to_string(
            "products/includes/product_card.html",
            {
                "product": product,
            },
        )

    def test_product_card_contains_name_and_link(self):
        html = self.render_card(
            self.regular_product,
        )

        self.assertIn(
            "MONO T-Shirt",
            html,
        )
        self.assertIn(
            reverse(
                "products:product_detail",
                args=[
                    self.regular_product.slug,
                ],
            ),
            html,
        )

    def test_product_card_displays_regular_price(self):
        html = self.render_card(
            self.regular_product,
        )

        self.assertIn(
            "2000.00",
            html,
        )

    def test_product_card_displays_discounted_price(self):
        html = self.render_card(
            self.discounted_product,
        )

        self.assertIn(
            "5000.00",
            html,
        )
        self.assertIn(
            "4500.00",
            html,
        )
