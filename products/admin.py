from django.contrib import admin

from .models import (
    Category,
    Gender,
    Product,
    ProductImage,
    ProductType,
    ProductVariant,
)


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "slug",
    )
    list_filter = ("category",)
    search_fields = (
        "name",
        "slug",
        "category__name",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    list_select_related = ("category",)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "product_type",
        "gender",
        "price",
        "discount",
        "is_popular",
        "created_at",
    )
    list_filter = (
        "category",
        "product_type",
        "gender",
        "is_popular",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    list_select_related = (
        "category",
        "product_type",
        "gender",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (
        ProductVariantInline,
        ProductImageInline,
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "color",
        "size",
        "stock",
        "is_in_stock",
    )
    list_filter = (
        "color",
        "size",
    )
    search_fields = (
        "product__name",
        "product__slug",
    )
    list_select_related = ("product",)

    @admin.display(
        boolean=True,
        description="В наличии",
    )
    def is_in_stock(self, obj):
        return obj.in_stock


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "alt_text",
    )
    search_fields = (
        "product__name",
        "alt_text",
    )
    list_select_related = ("product",)
