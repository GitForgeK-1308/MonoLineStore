from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from .services import change_order_status


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)

    def clean_status(self):
        new_status = self.cleaned_data["status"]

        if self.instance.pk is None:
            return new_status

        current_order = Order.objects.only(
            "status",
        ).get(
            pk=self.instance.pk,
        )

        if not current_order.can_transition_to(new_status):
            raise ValidationError(
                "Нельзя изменить статус "
                f"с «{current_order.get_status_display()}» "
                f"на «{Order.Status(new_status).label}»."
            )

        return new_status


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    fields = (
        "variant",
        "product_name",
        "product_slug",
        "color",
        "size",
        "price",
        "quantity",
        "item_total",
    )

    readonly_fields = fields

    @admin.display(description="Сумма")
    def item_total(self, obj):
        if obj.pk is None:
            return None

        return obj.total_price

    def has_add_permission(
        self,
        request,
        obj=None,
    ):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm

    list_display = (
        "id",
        "first_name",
        "email",
        "phone",
        "total_price",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "first_name",
        "phone",
        "email",
        "address",
        "user__email",
    )

    list_select_related = ("user",)

    date_hierarchy = "created_at"

    readonly_fields = (
        "user",
        "first_name",
        "phone",
        "email",
        "address",
        "comment",
        "total_price",
        "created_at",
        "updated_at",
    )

    inlines = (OrderItemInline,)

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if not change:
            super().save_model(
                request,
                obj,
                form,
                change,
            )
            return

        change_order_status(
            order_id=obj.pk,
            new_status=form.cleaned_data["status"],
        )

        obj.refresh_from_db()

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_name",
        "color",
        "size",
        "price",
        "quantity",
        "item_total",
    )

    search_fields = (
        "product_name",
        "product_slug",
        "order__email",
    )

    list_select_related = (
        "order",
        "variant",
    )

    readonly_fields = (
        "order",
        "variant",
        "product_name",
        "product_slug",
        "color",
        "size",
        "price",
        "quantity",
        "item_total",
    )

    @admin.display(description="Сумма")
    def item_total(self, obj):
        return obj.total_price

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False
