from decimal import Decimal, InvalidOperation

from django.http import Http404
from django.views.generic import ListView

from .models import Category, Gender, Product, ProductType
from .search import search_products


class ProductCatalogView(ListView):
    model = Product
    template_name = "products/catalog.html"
    context_object_name = "products"
    paginate_by = 9

    def get_current_category(self):
        category_slug = self.kwargs.get("category_slug")

        if not category_slug:
            return None

        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist as error:
            raise Http404("Категория не найдена.") from error

    def get_decimal_param(self, name):
        value = self.request.GET.get(name)

        if not value:
            return None

        try:
            return Decimal(value)
        except InvalidOperation:
            return None

    def get_queryset(self):
        products = Product.objects.select_related(
            "category",
            "product_type",
            "gender",
        )

        self.current_category = self.get_current_category()

        if self.current_category:
            products = products.filter(
                category=self.current_category,
            )

        product_type = self.request.GET.get("product_type")
        gender = self.request.GET.get("gender")
        query = self.request.GET.get("q", "").strip()

        if product_type:
            products = products.filter(
                product_type__slug=product_type,
            )

        if gender:
            products = products.filter(
                gender__slug=gender,
            )

        if self.request.GET.get("in_stock"):
            products = products.filter(
                variants__stock__gt=0,
            ).distinct()

        if self.request.GET.get("is_popular"):
            products = products.filter(
                is_popular=True,
            )

        if self.request.GET.get("discount"):
            products = products.filter(
                discount__gt=0,
            )

        min_price = self.get_decimal_param("min_price")
        max_price = self.get_decimal_param("max_price")

        if min_price is not None:
            products = products.filter(
                price__gte=min_price,
            )

        if max_price is not None:
            products = products.filter(
                price__lte=max_price,
            )

        if query:
            products = search_products(
                products,
                query,
            )

        ordering = self.request.GET.get("ordering")

        if ordering == "price_asc":
            products = products.order_by(
                "price",
                "id",
            )
        elif ordering == "price_desc":
            products = products.order_by(
                "-price",
                "id",
            )
        elif not query:
            products = products.order_by(
                "-created_at",
            )

        return products

    def get_product_types(self):
        product_types = ProductType.objects.select_related(
            "category",
        )

        if self.current_category:
            product_types = product_types.filter(
                category=self.current_category,
            )

        gender = self.request.GET.get("gender")

        if gender:
            product_types = product_types.filter(
                products__gender__slug=gender,
            ).distinct()

        return product_types

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context.update(
            {
                "categories": Category.objects.all(),
                "product_types": self.get_product_types(),
                "genders": Gender.objects.all(),
                "current_category": self.current_category,
                "query": self.request.GET.get("q", ""),
                "product_type": self.request.GET.get(
                    "product_type",
                ),
                "gender": self.request.GET.get("gender"),
                "in_stock": self.request.GET.get("in_stock"),
                "is_popular": self.request.GET.get(
                    "is_popular",
                ),
                "has_discount": self.request.GET.get(
                    "discount",
                ),
                "min_price": self.request.GET.get(
                    "min_price",
                ),
                "max_price": self.request.GET.get(
                    "max_price",
                ),
                "ordering": self.request.GET.get("ordering"),
                "query_params": query_params.urlencode(),
            }
        )

        return context
