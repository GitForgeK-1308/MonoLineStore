from decimal import Decimal

from django.template.loader import render_to_string
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse
from django.utils.formats import localize

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
            localize(self.regular_product.price),
            html,
        )

    def test_product_card_displays_discounted_price(self):
        html = self.render_card(
            self.discounted_product,
        )

        self.assertIn(
            localize(self.discounted_product.price),
            html,
        )
        self.assertIn(
            localize(
                self.discounted_product.discounted_price,
            ),
            html,
        )


class CatalogTemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Каталог",
            slug="catalog-template-category",
        )

        for number in range(10):
            Product.objects.create(
                category=cls.category,
                name=f"Catalog Product {number}",
                slug=f"catalog-product-{number}",
                price=Decimal("1000.00"),
                discount=10,
            )

    def test_catalog_includes_catalog_stylesheet(self):
        response = self.client.get(
            reverse("products:catalog"),
        )

        self.assertContains(
            response,
            static("products/css/catalog.css"),
        )

    def test_catalog_pagination_preserves_filters(self):
        response = self.client.get(
            reverse("products:catalog"),
            {
                "discount": "1",
            },
        )

        self.assertContains(
            response,
            "?discount=1&amp;page=2",
        )


class ProductDetailTemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Detail Category",
            slug="detail-template-category",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Detail Hoodie",
            slug="mono-detail-hoodie",
            price=Decimal("5000.00"),
        )

        cls.related_product = Product.objects.create(
            category=cls.category,
            name="MONO Related Hoodie",
            slug="mono-related-hoodie",
            price=Decimal("4500.00"),
        )

    def get_response(self):
        return self.client.get(
            reverse(
                "products:product_detail",
                args=[self.product.slug],
            ),
        )

    def test_product_detail_includes_stylesheet(self):
        response = self.get_response()

        self.assertContains(
            response,
            static("products/css/product_detail.css"),
        )

    def test_related_products_use_product_card(self):
        response = self.get_response()

        self.assertContains(
            response,
            "MONO Related Hoodie",
        )
        self.assertContains(
            response,
            'class="product-card"',
        )

    def test_product_detail_includes_variant_script(self):
        response = self.get_response()

        self.assertContains(
            response,
            static("products/js/product_detail.js"),
        )
