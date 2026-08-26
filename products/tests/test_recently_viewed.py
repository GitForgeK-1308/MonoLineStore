from decimal import Decimal

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from products.models import Category, Product
from products.recently_viewed import (
    VIEWED_PRODUCTS_LIMIT,
    VIEWED_PRODUCTS_SESSION_KEY,
    add_viewed_product,
    get_viewed_products,
)


class RecentlyViewedProductsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )

        cls.products = [
            Product.objects.create(
                category=cls.category,
                name=f"Product {number}",
                slug=f"product-{number}",
                price=Decimal("1000.00"),
            )
            for number in range(6)
        ]

    def setUp(self):
        self.request = RequestFactory().get("/")

        middleware = SessionMiddleware(
            lambda request: None,
        )
        middleware.process_request(self.request)
        self.request.session.save()

    def test_add_viewed_product_saves_product_id(self):
        product = self.products[0]

        add_viewed_product(
            self.request,
            product.id,
        )

        self.assertEqual(
            self.request.session[VIEWED_PRODUCTS_SESSION_KEY],
            [product.id],
        )

    def test_latest_product_is_first(self):
        first = self.products[0]
        second = self.products[1]

        add_viewed_product(
            self.request,
            first.id,
        )
        add_viewed_product(
            self.request,
            second.id,
        )

        self.assertEqual(
            self.request.session[VIEWED_PRODUCTS_SESSION_KEY],
            [
                second.id,
                first.id,
            ],
        )

    def test_duplicate_product_is_moved_to_beginning(self):
        first = self.products[0]
        second = self.products[1]

        add_viewed_product(
            self.request,
            first.id,
        )
        add_viewed_product(
            self.request,
            second.id,
        )
        add_viewed_product(
            self.request,
            first.id,
        )

        self.assertEqual(
            self.request.session[VIEWED_PRODUCTS_SESSION_KEY],
            [
                first.id,
                second.id,
            ],
        )

    def test_viewed_products_are_limited(self):
        for product in self.products:
            add_viewed_product(
                self.request,
                product.id,
            )

        viewed_ids = self.request.session[VIEWED_PRODUCTS_SESSION_KEY]

        self.assertEqual(
            len(viewed_ids),
            VIEWED_PRODUCTS_LIMIT,
        )

    def test_get_viewed_products_preserves_session_order(self):
        first = self.products[0]
        second = self.products[1]
        third = self.products[2]

        self.request.session[VIEWED_PRODUCTS_SESSION_KEY] = [
            third.id,
            first.id,
            second.id,
        ]

        products = get_viewed_products(
            self.request,
        )

        self.assertEqual(
            products,
            [
                third,
                first,
                second,
            ],
        )

    def test_get_viewed_products_excludes_current_product(self):
        first = self.products[0]
        second = self.products[1]

        self.request.session[VIEWED_PRODUCTS_SESSION_KEY] = [
            first.id,
            second.id,
        ]

        products = get_viewed_products(
            self.request,
            exclude_product_id=first.id,
        )

        self.assertEqual(
            products,
            [second],
        )

    def test_deleted_product_is_ignored(self):
        first = self.products[0]
        second = self.products[1]

        self.request.session[VIEWED_PRODUCTS_SESSION_KEY] = [
            first.id,
            second.id,
        ]

        second.delete()

        products = get_viewed_products(
            self.request,
        )

        self.assertEqual(
            products,
            [first],
        )
