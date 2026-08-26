from django.test import TestCase

from accounts.forms import UserLoginForm, UserRegisterForm
from accounts.models import CustomUser


class UserRegisterFormTests(TestCase):
    def test_form_is_valid_with_correct_data(self):
        form = UserRegisterForm(
            data={
                "email": "user@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_creates_user(self):
        form = UserRegisterForm(
            data={
                "email": "user@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("StrongPassword123!"))

    def test_form_rejects_duplicate_email(self):
        CustomUser.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

        form = UserRegisterForm(
            data={
                "email": "user@example.com",
                "password1": "AnotherPassword123!",
                "password2": "AnotherPassword123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_rejects_different_passwords(self):
        form = UserRegisterForm(
            data={
                "email": "user@example.com",
                "password1": "StrongPassword123!",
                "password2": "AnotherPassword123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_email_field_uses_email_input(self):
        form = UserRegisterForm()

        self.assertEqual(
            form.fields["email"].widget.input_type,
            "email",
        )


class UserLoginFormTests(TestCase):
    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password=self.password,
        )

    def test_form_is_valid_with_correct_credentials(self):
        form = UserLoginForm(
            data={
                "username": "user@example.com",
                "password": self.password,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_user(),
            self.user,
        )

    def test_form_rejects_wrong_password(self):
        form = UserLoginForm(
            data={
                "username": "user@example.com",
                "password": "WrongPassword123!",
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_rejects_unknown_email(self):
        form = UserLoginForm(
            data={
                "username": "unknown@example.com",
                "password": self.password,
            }
        )

        self.assertFalse(form.is_valid())
