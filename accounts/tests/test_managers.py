from django.test import TestCase

from accounts.models import CustomUser


class UserManagerTests(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="strong-password-123",
        )

        self.assertEqual(
            user.email,
            "user@example.com",
        )
        self.assertTrue(user.check_password("strong-password-123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_normalizes_email(self):
        user = CustomUser.objects.create_user(
            email="User@EXAMPLE.COM",
            password="strong-password-123",
        )

        self.assertEqual(
            user.email,
            "User@example.com",
        )

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Email обязателен.",
        ):
            CustomUser.objects.create_user(
                email="",
                password="strong-password-123",
            )

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="strong-password-123",
        )

        self.assertEqual(
            user.email,
            "admin@example.com",
        )
        self.assertTrue(user.check_password("strong-password-123"))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Суперпользователь должен иметь is_staff=True.",
        ):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="strong-password-123",
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Суперпользователь должен иметь is_superuser=True.",
        ):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="strong-password-123",
                is_superuser=False,
            )