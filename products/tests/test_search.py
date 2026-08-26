from decimal import Decimal

from django.test import TestCase

from products.models import Category, Product
from products.search import search_products


class ProductSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.clothes = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )
        cls.shoes = Category.objects.create(
            name="Обувь",
            slug="shoes",
        )

        cls.hoodie = Product.objects.create(
            category=cls.clothes,
            name="MONO Hoodie",
            slug="mono-hoodie",
            description="Черное худи из хлопка",
            price=Decimal("4990.00"),
        )

        cls.t_shirt = Product.objects.create(
            category=cls.clothes,
            name="MONO T-Shirt",
            slug="mono-t-shirt",
            description="Базовая футболка",
            price=Decimal("1990.00"),
        )

        cls.sneakers = Product.objects.create(
            category=cls.shoes,
            name="MONO Sneakers",
            slug="mono-sneakers",
            description="Черные городские кроссовки",
            price=Decimal("7990.00"),
        )

    def test_search_finds_product_by_name(self):
        products = search_products(
            Product.objects.all(),
            "Hoodie",
        )

        self.assertQuerySetEqual(
            products,
            [self.hoodie],
        )

    def test_search_finds_product_by_description(self):
        products = search_products(
            Product.objects.all(),
            "кроссовки",
        )

        self.assertQuerySetEqual(
            products,
            [self.sneakers],
        )

    def test_search_by_id(self):
        products = search_products(
            Product.objects.all(),
            str(self.t_shirt.pk),
        )

        self.assertQuerySetEqual(
            products,
            [self.t_shirt],
        )

    def test_search_preserves_existing_queryset_filters(self):
        queryset = Product.objects.filter(
            category=self.clothes,
        )

        products = search_products(
            queryset,
            "MONO",
        )

        self.assertIn(
            self.hoodie,
            products,
        )
        self.assertIn(
            self.t_shirt,
            products,
        )
        self.assertNotIn(
            self.sneakers,
            products,
        )

    def test_empty_search_returns_original_queryset(self):
        queryset = Product.objects.filter(
            category=self.clothes,
        )

        products = search_products(
            queryset,
            "   ",
        )

        self.assertQuerySetEqual(
            products,
            list(queryset),
        )
