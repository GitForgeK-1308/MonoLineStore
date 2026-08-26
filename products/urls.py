from django.urls import path

from .views import ProductCatalogView

app_name = "products"

urlpatterns = [
    path(
        "catalog/",
        ProductCatalogView.as_view(),
        name="catalog",
    ),
    path(
        "catalog/<slug:category_slug>/",
        ProductCatalogView.as_view(),
        name="catalog",
    ),
]
