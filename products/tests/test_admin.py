from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

User = get_user_model()


class ProductAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongAdminPassword123!",
        )

        cls.category = Category.objects.create(
            name="Одежда",
            slug="clothes-admin",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="MONO Admin Hoodie",
            slug="mono-admin-hoodie",
            price=Decimal("4990.00"),
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_product_changelist_is_available(self):
        response = self.client.get(
            reverse("admin:products_product_changelist"),
        )

        self.assertEqual(response.status_code, 200)

    def test_product_is_displayed_in_admin(self):
        response = self.client.get(
            reverse("admin:products_product_changelist"),
        )

        self.assertContains(
            response,
            self.product.name,
        )

    def test_product_add_page_is_available(self):
        response = self.client.get(
            reverse("admin:products_product_add"),
        )

        self.assertEqual(response.status_code, 200)

    def test_product_change_page_is_available(self):
        response = self.client.get(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_product_change_page_contains_variant_inline(self):
        response = self.client.get(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            )
        )

        self.assertContains(
            response,
            "Варианты товара",
        )

    def test_product_change_page_contains_image_inline(self):
        response = self.client.get(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            )
        )

        self.assertContains(
            response,
            "Изображения товара",
        )
