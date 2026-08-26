from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import UserLoginForm
from .views import UserProfileView, UserRegisterView

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
]
