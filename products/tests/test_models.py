from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from products.models import (
    Category,
    Gender,
    Product,
    ProductImage,
    ProductType,
    ProductVariant,
)


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )
        cls.product_type = ProductType.objects.create(
            category=cls.category,
            name="Футболки",
            slug="t-shirts",
        )
        cls.gender = Gender.objects.create(
            name="Мужское",
            slug="men",
        )

    def create_product(self, **kwargs):
        data = {
            "category": self.category,
            "product_type": self.product_type,
            "gender": self.gender,
            "name": "MONO T-Shirt",
            "slug": "mono-t-shirt",
            "price": Decimal("999.95"),
        }
        data.update(kwargs)

        return Product.objects.create(**data)

    def test_product_string_representation(self):
        product = self.create_product()

        self.assertEqual(
            str(product),
            "MONO T-Shirt",
        )

    def test_product_without_discount_returns_original_price(self):
        product = self.create_product(
            discount=0,
        )

        self.assertEqual(
            product.discounted_price,
            Decimal("999.95"),
        )

    def test_discounted_price_is_calculated_and_rounded(self):
        product = self.create_product(
            discount=15,
        )

        self.assertEqual(
            product.discounted_price,
            Decimal("849.96"),
        )

    def test_total_stock_is_sum_of_variants(self):
        product = self.create_product()

        ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=3,
        )
        ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.L,
            stock=7,
        )

        self.assertEqual(
            product.total_stock,
            10,
        )

    def test_product_is_in_stock_when_variant_has_stock(self):
        product = self.create_product()

        ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=0,
        )
        ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.L,
            stock=2,
        )

        self.assertTrue(product.in_stock)

    def test_product_is_not_in_stock_when_all_variants_are_empty(self):
        product = self.create_product()

        ProductVariant.objects.create(
            product=product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=0,
        )

        self.assertFalse(product.in_stock)

    def test_product_type_must_belong_to_product_category(self):
        another_category = Category.objects.create(
            name="Обувь",
            slug="shoes",
        )
        another_type = ProductType.objects.create(
            category=another_category,
            name="Кроссовки",
            slug="sneakers",
        )

        product = Product(
            category=self.category,
            product_type=another_type,
            name="Incorrect Product",
            slug="incorrect-product",
            price=Decimal("1000.00"),
        )

        with self.assertRaises(ValidationError) as context:
            product.full_clean()

        self.assertIn(
            "product_type",
            context.exception.message_dict,
        )

    def test_product_price_must_be_positive(self):
        product = Product(
            category=self.category,
            name="Free Product",
            slug="free-product",
            price=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_discount_cannot_be_greater_than_100(self):
        product = Product(
            category=self.category,
            name="Invalid Discount",
            slug="invalid-discount",
            price=Decimal("1000.00"),
            discount=101,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()


class ProductVariantModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )

        cls.product = Product.objects.create(
            category=category,
            name="MONO Hoodie",
            slug="mono-hoodie",
            price=Decimal("4990.00"),
        )

    def test_variant_is_in_stock(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        self.assertTrue(variant.in_stock)

    def test_variant_is_not_in_stock_when_stock_is_zero(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=0,
        )

        self.assertFalse(variant.in_stock)

    def test_duplicate_product_color_and_size_is_not_allowed(self):
        ProductVariant.objects.create(
            product=self.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductVariant.objects.create(
                    product=self.product,
                    color=ProductVariant.Color.BLACK,
                    size=ProductVariant.Size.M,
                    stock=10,
                )

    def test_variant_string_representation(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        self.assertEqual(
            str(variant),
            "MONO Hoodie / Черный / M",
        )


class ProductRelationsTests(TestCase):
    def test_category_with_product_cannot_be_deleted(self):
        category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )
        product = Product.objects.create(
            category=category,
            name="MONO T-Shirt",
            slug="mono-t-shirt",
            price=Decimal("1990.00"),
        )

        with self.assertRaises(ProtectedError):
            category.delete()

        self.assertTrue(
            Product.objects.filter(pk=product.pk).exists()
        )

    def test_product_image_string_representation(self):
        category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )
        product = Product.objects.create(
            category=category,
            name="MONO T-Shirt",
            slug="mono-t-shirt",
            price=Decimal("1990.00"),
        )

        image = ProductImage.objects.create(
            product=product,
            image="products/gallery/t-shirt.jpg",
            alt_text="Черная футболка MONO",
        )

        self.assertEqual(
            str(image),
            "Изображение для MONO T-Shirt",
        )