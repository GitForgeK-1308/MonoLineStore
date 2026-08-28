from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView

from .forms import UserRegisterForm, UserSetPasswordForm
from .password_validation import get_password_requirements

User = get_user_model()

PASSWORD_VALIDATION_USER_SESSION_KEY = "accounts_password_validation_user_id"


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:profile")

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )


class UserProfileView(
    LoginRequiredMixin,
    TemplateView,
):
    template_name = "accounts/profile.html"


class UserPasswordResetConfirmView(
    auth_views.PasswordResetConfirmView,
):
    template_name = "accounts/password_reset_confirm.html"
    form_class = UserSetPasswordForm
    success_url = reverse_lazy(
        "accounts:password_reset_complete",
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        self.request.session[PASSWORD_VALIDATION_USER_SESSION_KEY] = str(self.user.pk)

        return kwargs

    def form_valid(self, form):
        self.request.session.pop(
            PASSWORD_VALIDATION_USER_SESSION_KEY,
            None,
        )

        return super().form_valid(form)


@sensitive_post_parameters("password")
@never_cache
@require_POST
def password_check(request):
    password = request.POST.get(
        "password",
        "",
    )

    mode = request.POST.get(
        "mode",
        "register",
    )

    user = None

    if mode == "register":
        email = request.POST.get(
            "email",
            "",
        ).strip()

        if email:
            user = User(
                email=email,
            )

    elif mode == "reset":
        user_id = request.session.get(
            PASSWORD_VALIDATION_USER_SESSION_KEY,
        )

        if not user_id:
            return JsonResponse(
                {
                    "detail": ("Не удалось определить пользователя."),
                },
                status=400,
            )

        user = User.objects.filter(
            pk=user_id,
        ).first()

        if user is None:
            return JsonResponse(
                {
                    "detail": "Пользователь не найден.",
                },
                status=400,
            )

    else:
        return JsonResponse(
            {
                "detail": "Некорректный режим проверки.",
            },
            status=400,
        )

    requirements = get_password_requirements(
        password,
        user=user,
    )

    if mode == "register" and user is None:
        requirements["similarity"] = None

    return JsonResponse(
        {
            "requirements": requirements,
        }
    )
