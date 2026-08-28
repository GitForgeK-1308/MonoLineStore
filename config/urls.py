from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("", include("core.urls")),
    path("", include("products.urls")),
]

if settings.DEBUG and settings.DEBUG_TOOLBAR_ENABLED:
    import debug_toolbar

    urlpatterns += [
        path(
            "__debug__/",
            include(debug_toolbar.urls),
        ),
    ]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
