from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class UserRegisterViewTests(TestCase):
    def test_register_page_is_available(self):
        response = self.client.get(
            reverse("accounts:register"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/register.html",
        )

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "email": "user@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CustomUser.objects.filter(
                email="user@example.com",
            ).exists()
        )

    def test_register_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "email": "user@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:login"),
        )

    def test_authenticated_user_is_redirected_from_register(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:register"),
        )

        self.assertRedirects(
            response,
            reverse("accounts:profile"),
        )


class UserProfileViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

    def test_profile_requires_authentication(self):
        response = self.client.get(
            reverse("accounts:profile"),
        )

        expected_url = (
            f"{reverse('accounts:login')}"
            f"?next={reverse('accounts:profile')}"
        )

        self.assertRedirects(
            response,
            expected_url,
        )

    def test_authenticated_user_can_open_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:profile"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/profile.html",
        )


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password=self.password,
        )

    def test_login_page_is_available(self):
        response = self.client.get(
            reverse("accounts:login"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/login.html",
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "user@example.com",
                "password": self.password,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:profile"),
        )

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "user@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )


class UserLogoutViewTests(TestCase):
    def test_authenticated_user_can_logout(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:logout"),
        )

        self.assertRedirects(
            response,
            reverse("accounts:login"),
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )