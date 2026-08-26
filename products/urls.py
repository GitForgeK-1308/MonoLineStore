from django.urls import path

from .views import ProductCatalogView, ProductDetailView

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
    path(
        "product/<slug:product_slug>/",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
]
