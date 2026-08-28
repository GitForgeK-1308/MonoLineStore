from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
)
from django.template import loader

from .tasks import send_password_reset_email

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "Email"
        self.fields["email"].help_text = "Укажите действующий email."
        self.fields["email"].widget = forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Введите email",
                "autocomplete": "email",
            }
        )
        self.fields["email"].error_messages.update(
            {
                "required": "Введите email.",
                "invalid": "Введите корректный email.",
                "unique": "Пользователь с таким email уже существует.",
            }
        )

        self.fields["password1"].label = "Пароль"
        self.fields["password1"].help_text = password_validators_help_text_html()
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Введите пароль",
                "autocomplete": "new-password",
            }
        )

        self.fields["password2"].label = "Повтор пароля"
        self.fields["password2"].help_text = "Введите тот же пароль ещё раз."
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Повторите пароль",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].error_messages.update(
            {
                "required": "Повторите пароль.",
            }
        )


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Введите email",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Введите пароль",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Неверный email или пароль.",
        "inactive": "Этот аккаунт неактивен.",
    }


class AsyncPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Введите email",
                "autocomplete": "email",
            }
        ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(
            subject_template_name,
            context,
        )

        subject = "".join(
            subject.splitlines(),
        )

        body = loader.render_to_string(
            email_template_name,
            context,
        )

        html_body = None

        if html_email_template_name:
            html_body = loader.render_to_string(
                html_email_template_name,
                context,
            )

        send_password_reset_email.delay(
            subject,
            body,
            from_email,
            to_email,
            html_body,
        )


class UserSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].label = "Новый пароль"
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Введите новый пароль",
                "autocomplete": "new-password",
            }
        )

        self.fields["new_password2"].label = "Повтор пароля"
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Повторите новый пароль",
                "autocomplete": "new-password",
            }
        )
