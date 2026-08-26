from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import (
    Category,
    Gender,
    Product,
    ProductType,
    ProductVariant,
)


class ProductCatalogViewTests(TestCase):
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

        cls.hoodies = ProductType.objects.create(
            category=cls.clothes,
            name="Худи",
            slug="hoodies",
        )
        cls.t_shirts = ProductType.objects.create(
            category=cls.clothes,
            name="Футболки",
            slug="t-shirts",
        )
        cls.sneakers_type = ProductType.objects.create(
            category=cls.shoes,
            name="Кроссовки",
            slug="sneakers",
        )

        cls.men = Gender.objects.create(
            name="Мужское",
            slug="men",
        )
        cls.women = Gender.objects.create(
            name="Женское",
            slug="women",
        )

        cls.hoodie = Product.objects.create(
            category=cls.clothes,
            product_type=cls.hoodies,
            gender=cls.men,
            name="MONO Hoodie",
            slug="mono-hoodie",
            description="Черное хлопковое худи",
            price=Decimal("5000.00"),
            discount=10,
            is_popular=True,
        )

        cls.t_shirt = Product.objects.create(
            category=cls.clothes,
            product_type=cls.t_shirts,
            gender=cls.women,
            name="Basic T-Shirt",
            slug="basic-t-shirt",
            description="Базовая футболка",
            price=Decimal("2000.00"),
        )

        cls.sneakers = Product.objects.create(
            category=cls.shoes,
            product_type=cls.sneakers_type,
            gender=cls.men,
            name="MONO Sneakers",
            slug="mono-sneakers",
            description="Городские кроссовки",
            price=Decimal("7000.00"),
        )

        ProductVariant.objects.create(
            product=cls.hoodie,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        ProductVariant.objects.create(
            product=cls.t_shirt,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.M,
            stock=0,
        )

        ProductVariant.objects.create(
            product=cls.sneakers,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.L,
            stock=2,
        )

    def test_catalog_page_is_available(self):
        response = self.client.get(
            reverse("products:catalog"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "products/catalog.html",
        )

    def test_catalog_filters_by_category(self):
        response = self.client.get(
            reverse(
                "products:catalog",
                kwargs={"category_slug": "clothes"},
            )
        )

        products = response.context["products"]

        self.assertIn(self.hoodie, products)
        self.assertIn(self.t_shirt, products)
        self.assertNotIn(self.sneakers, products)

    def test_unknown_category_returns_404(self):
        response = self.client.get(
            reverse(
                "products:catalog",
                kwargs={"category_slug": "unknown"},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_catalog_filters_by_product_type(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"product_type": "hoodies"},
        )

        products = response.context["products"]

        self.assertQuerySetEqual(
            products,
            [self.hoodie],
        )

    def test_catalog_filters_by_gender(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"gender": "women"},
        )

        products = response.context["products"]

        self.assertQuerySetEqual(
            products,
            [self.t_shirt],
        )

    def test_catalog_filters_products_in_stock(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"in_stock": "1"},
        )

        products = response.context["products"]

        self.assertIn(self.hoodie, products)
        self.assertIn(self.sneakers, products)
        self.assertNotIn(self.t_shirt, products)

    def test_catalog_filters_popular_products(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"is_popular": "1"},
        )

        self.assertQuerySetEqual(
            response.context["products"],
            [self.hoodie],
        )

    def test_catalog_filters_discounted_products(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"discount": "1"},
        )

        self.assertQuerySetEqual(
            response.context["products"],
            [self.hoodie],
        )

    def test_catalog_filters_by_price_range(self):
        response = self.client.get(
            reverse("products:catalog"),
            {
                "min_price": "4000",
                "max_price": "6000",
            },
        )

        self.assertQuerySetEqual(
            response.context["products"],
            [self.hoodie],
        )

    def test_invalid_price_does_not_break_catalog(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"min_price": "not-a-number"},
        )

        self.assertEqual(response.status_code, 200)

    def test_catalog_orders_by_price_ascending(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"ordering": "price_asc"},
        )

        products = list(response.context["products"])

        self.assertEqual(
            products,
            [
                self.t_shirt,
                self.hoodie,
                self.sneakers,
            ],
        )

    def test_catalog_orders_by_price_descending(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"ordering": "price_desc"},
        )

        products = list(response.context["products"])

        self.assertEqual(
            products,
            [
                self.sneakers,
                self.hoodie,
                self.t_shirt,
            ],
        )

    def test_search_preserves_category_filter(self):
        response = self.client.get(
            reverse(
                "products:catalog",
                kwargs={"category_slug": "clothes"},
            ),
            {"q": "MONO"},
        )

        products = response.context["products"]

        self.assertIn(self.hoodie, products)
        self.assertNotIn(self.sneakers, products)

    def test_product_types_are_filtered_by_category(self):
        response = self.client.get(
            reverse(
                "products:catalog",
                kwargs={"category_slug": "clothes"},
            )
        )

        product_types = response.context["product_types"]

        self.assertIn(self.hoodies, product_types)
        self.assertIn(self.t_shirts, product_types)
        self.assertNotIn(
            self.sneakers_type,
            product_types,
        )

    def test_catalog_is_paginated_by_nine_products(self):
        for number in range(10):
            Product.objects.create(
                category=self.clothes,
                name=f"Product {number}",
                slug=f"product-{number}",
                price=Decimal("1000.00"),
            )

        response = self.client.get(
            reverse("products:catalog"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].number,
            2,
        )
        self.assertEqual(
            response.context["paginator"].per_page,
            9,
        )


class ProductDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="clothes-detail",
        )

        cls.other_category = Category.objects.create(
            name="Обувь",
            slug="shoes-detail",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Hoodie Detail",
            slug="mono-hoodie-detail",
            description="Черное худи",
            price=Decimal("4990.00"),
        )

        ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        cls.out_of_stock_product = Product.objects.create(
            category=cls.category,
            name="Empty T-Shirt",
            slug="empty-t-shirt",
            price=Decimal("1990.00"),
        )

        ProductVariant.objects.create(
            product=cls.out_of_stock_product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.M,
            stock=0,
        )

        cls.related_products = [
            Product.objects.create(
                category=cls.category,
                name=f"Related Product {number}",
                slug=f"related-product-{number}",
                price=Decimal("2500.00"),
            )
            for number in range(5)
        ]

        cls.unrelated_product = Product.objects.create(
            category=cls.other_category,
            name="Unrelated Sneakers",
            slug="unrelated-sneakers",
            price=Decimal("7000.00"),
        )

    def test_product_detail_page_is_available(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "products/product_detail.html",
        )
        self.assertEqual(
            response.context["product"],
            self.product,
        )

    def test_unknown_product_returns_404(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": "unknown-product",
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_detail_contains_add_to_cart_form(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        form = response.context["form"]

        self.assertEqual(
            form.product,
            self.product,
        )

    def test_product_with_stock_has_stock(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        self.assertTrue(
            response.context["has_stock"],
        )

    def test_product_without_stock_has_no_stock(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.out_of_stock_product.slug,
                },
            )
        )

        self.assertFalse(
            response.context["has_stock"],
        )

    def test_opened_product_is_saved_to_recently_viewed(self):
        self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        session = self.client.session

        self.assertEqual(
            session["viewed_products"][0],
            self.product.pk,
        )

    def test_previous_product_appears_in_recently_viewed(self):
        first_product = self.related_products[0]

        self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": first_product.slug,
                },
            )
        )

        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        viewed_products = response.context["viewed_products"]

        self.assertIn(
            first_product,
            viewed_products,
        )
        self.assertNotIn(
            self.product,
            viewed_products,
        )

    def test_related_products_are_from_same_category(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={
                    "product_slug": self.product.slug,
                },
            )
        )

        related_products = list(response.context["related_products"])

        self.assertNotIn(
            self.product,
            related_products,
        )
        self.assertNotIn(
            self.unrelated_product,
            related_products,
        )
        self.assertEqual(
            len(related_products),
            4,
        )
