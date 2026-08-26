from django.contrib import admin

from .models import Order, OrderItem


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

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
