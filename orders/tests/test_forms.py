from django.test import TestCase

from orders.forms import OrderCreateForm


class OrderCreateFormTests(TestCase):
    def get_valid_data(self):
        return {
            "first_name": "Иван",
            "phone": "+79990000000",
            "email": "customer@example.com",
            "address": "Москва, ул. Примерная, 10",
            "comment": "Позвонить перед доставкой",
        }

    def test_form_is_valid(self):
        form = OrderCreateForm(
            data=self.get_valid_data(),
        )

        self.assertTrue(form.is_valid())

    def test_comment_is_optional(self):
        data = self.get_valid_data()
        data["comment"] = ""

        form = OrderCreateForm(
            data=data,
        )

        self.assertTrue(form.is_valid())

    def test_first_name_is_required(self):
        data = self.get_valid_data()
        data["first_name"] = ""

        form = OrderCreateForm(
            data=data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "first_name",
            form.errors,
        )

    def test_phone_is_required(self):
        data = self.get_valid_data()
        data["phone"] = ""

        form = OrderCreateForm(
            data=data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "phone",
            form.errors,
        )

    def test_invalid_email_is_rejected(self):
        data = self.get_valid_data()
        data["email"] = "not-an-email"

        form = OrderCreateForm(
            data=data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "email",
            form.errors,
        )

    def test_form_does_not_expose_system_fields(self):
        form = OrderCreateForm()

        self.assertEqual(
            list(form.fields),
            [
                "first_name",
                "phone",
                "email",
                "address",
                "comment",
            ],
        )

        self.assertNotIn(
            "total_price",
            form.fields,
        )
        self.assertNotIn(
            "status",
            form.fields,
        )
        self.assertNotIn(
            "user",
            form.fields,
        )

    def test_invalid_phone_is_rejected(self):
        data = self.get_valid_data()
        data["phone"] = "abc123"

        form = OrderCreateForm(
            data=data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "phone",
            form.errors,
        )
