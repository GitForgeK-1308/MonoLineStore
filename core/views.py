from django.views.generic import TemplateView

from products.models import Product


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all()

        context["popular_products"] = products.filter(
            is_popular=True,
        )[:8]

        context["new_products"] = products.order_by(
            "-created_at",
        )[:8]

        return context
