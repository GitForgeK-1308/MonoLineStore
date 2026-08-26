from decimal import Decimal

from django.test import TestCase

from products.forms import AddToCartForm
from products.models import (
    Category,
    Product,
    ProductVariant,
)


class AddToCartFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(
            name="Одежда",
            slug="clothes",
        )

        cls.product = Product.objects.create(
            category=category,
            name="MONO T-Shirt",
            slug="mono-t-shirt",
            price=Decimal("1990.00"),
        )

        cls.black_m = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.BLACK,
            size=ProductVariant.Size.M,
            stock=5,
        )

        cls.white_l = ProductVariant.objects.create(
            product=cls.product,
            color=ProductVariant.Color.WHITE,
            size=ProductVariant.Size.L,
            stock=0,
        )

    def test_form_is_valid_for_available_variant(self):
        form = AddToCartForm(
            data={
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.M,
                "quantity": 2,
            },
            product=self.product,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["variant"],
            self.black_m,
        )

    def test_form_rejects_nonexistent_combination(self):
        form = AddToCartForm(
            data={
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.L,
                "quantity": 1,
            },
            product=self.product,
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "Такого варианта товара не существует.",
            form.non_field_errors(),
        )

    def test_form_rejects_out_of_stock_variant(self):
        form = AddToCartForm(
            data={
                "color": ProductVariant.Color.WHITE,
                "size": ProductVariant.Size.L,
                "quantity": 1,
            },
            product=self.product,
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "Этот вариант товара закончился.",
            form.non_field_errors(),
        )

    def test_form_rejects_quantity_greater_than_stock(self):
        form = AddToCartForm(
            data={
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.M,
                "quantity": 10,
            },
            product=self.product,
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "Доступно только 5 шт.",
            form.non_field_errors(),
        )

    def test_quantity_cannot_be_less_than_one(self):
        form = AddToCartForm(
            data={
                "color": ProductVariant.Color.BLACK,
                "size": ProductVariant.Size.M,
                "quantity": 0,
            },
            product=self.product,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "quantity",
            form.errors,
        )

    def test_form_contains_only_product_colors_and_sizes(self):
        form = AddToCartForm(
            product=self.product,
        )

        colors = [
            value
            for value, _ in form.fields["color"].choices
        ]
        sizes = [
            value
            for value, _ in form.fields["size"].choices
        ]

        self.assertEqual(
            set(colors),
            {
                ProductVariant.Color.BLACK,
                ProductVariant.Color.WHITE,
            },
        )
        self.assertEqual(
            set(sizes),
            {
                ProductVariant.Size.M,
                ProductVariant.Size.L,
            },
        )

    def test_form_without_product_is_invalid(self):
        form = AddToCartForm(
            data={
                "quantity": 1,
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "Товар не найден.",
            form.non_field_errors(),
        )