from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import AsyncPasswordResetForm, UserLoginForm
from .views import (
    UserPasswordResetConfirmView,
    UserProfileView,
    UserRegisterView,
    password_check,
)

app_name = "accounts"

urlpatterns = [
    path(
        "register/",
        UserRegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=UserLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "profile/",
        UserProfileView.as_view(),
        name="profile",
    ),
    path(
        "password-check/",
        password_check,
        name="password_check",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            form_class=AsyncPasswordResetForm,
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy(
                "accounts:password_reset_done",
            ),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
