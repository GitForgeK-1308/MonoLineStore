from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import CustomUser


class CustomUserModelTests(TestCase):
    def test_user_string_representation_is_email(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="strong-password-123",
        )

        self.assertEqual(
            str(user),
            "user@example.com",
        )

    def test_email_is_unique(self):
        CustomUser.objects.create_user(
            email="user@example.com",
            password="strong-password-123",
        )

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                email="user@example.com",
                password="another-password-123",
            )

    def test_username_field_does_not_exist(self):
        with self.assertRaises(FieldDoesNotExist):
            CustomUser._meta.get_field("username")
