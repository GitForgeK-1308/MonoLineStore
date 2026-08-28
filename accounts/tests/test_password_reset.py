from unittest.mock import patch
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.email = "reset@example.com"
        self.old_password = "StrongPassword123!"
        self.new_password = "NewStrongPassword456!"

        self.user = CustomUser.objects.create_user(
            email=self.email,
            password=self.old_password,
        )

    @patch(
        "accounts.forms.send_password_reset_email.delay",
    )
    def test_password_reset_request_uses_celery(
        self,
        delay_mock,
    ):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {
                "email": self.email,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_done"),
        )

        delay_mock.assert_called_once()

        task_args = delay_mock.call_args.args

        self.assertEqual(
            task_args[3],
            self.email,
        )

    @patch(
        "accounts.forms.send_password_reset_email.delay",
    )
    def test_unknown_email_does_not_reveal_account_exists(
        self,
        delay_mock,
    ):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {
                "email": "unknown@example.com",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_done"),
        )

        delay_mock.assert_not_called()

    @patch(
        "accounts.forms.send_password_reset_email.delay",
    )
    def test_user_can_reset_password_and_login(
        self,
        delay_mock,
    ):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {
                "email": self.email,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_done"),
        )

        delay_mock.assert_called_once()

        email_body = delay_mock.call_args.args[1]

        reset_url = next(
            line.strip()
            for line in email_body.splitlines()
            if line.strip().startswith(
                (
                    "http://",
                    "https://",
                )
            )
        )

        reset_path = urlsplit(reset_url).path

        response = self.client.get(
            reset_path,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        set_password_path = response["Location"]

        response = self.client.post(
            set_password_path,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_complete"),
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password(
                self.old_password,
            )
        )

        self.assertTrue(
            self.user.check_password(
                self.new_password,
            )
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.email,
                "password": self.new_password,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:profile"),
        )
