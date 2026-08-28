from django import forms

from .models import ProductVariant


class AddToCartForm(forms.Form):
    color = forms.ChoiceField(
        label="Цвет",
        widget=forms.RadioSelect,
    )
    size = forms.ChoiceField(
        label="Размер",
        widget=forms.RadioSelect,
    )
    quantity = forms.IntegerField(
        label="Количество",
        min_value=1,
        initial=1,
    )

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.product = product
        self.available_colors = []
        self.available_sizes = []
        self.available_combinations = []

        if product is None:
            self.fields["color"].choices = []
            self.fields["size"].choices = []
            return

        all_variants = list(product.variants.all())

        available_variants = [variant for variant in all_variants if variant.in_stock]

        all_colors = {variant.color for variant in all_variants}

        all_sizes = {variant.size for variant in all_variants}

        self.available_colors = list(
            dict.fromkeys(variant.color for variant in available_variants)
        )

        self.available_sizes = list(
            dict.fromkeys(variant.size for variant in available_variants)
        )

        self.available_combinations = [
            {
                "color": variant.color,
                "size": variant.size,
                "stock": variant.stock,
            }
            for variant in available_variants
        ]

        self.fields["color"].choices = [
            (value, label)
            for value, label in ProductVariant.Color.choices
            if value in all_colors
        ]

        self.fields["size"].choices = [
            (value, label)
            for value, label in ProductVariant.Size.choices
            if value in all_sizes
        ]

    def clean(self):
        cleaned_data = super().clean()

        if self.product is None:
            raise forms.ValidationError("Товар не найден.")

        color = cleaned_data.get("color")
        size = cleaned_data.get("size")
        quantity = cleaned_data.get("quantity")

        if not color or not size or quantity is None:
            return cleaned_data

        try:
            variant = ProductVariant.objects.get(
                product=self.product,
                color=color,
                size=size,
            )
        except ProductVariant.DoesNotExist as error:
            raise forms.ValidationError(
                "Такого варианта товара не существует."
            ) from error

        if not variant.in_stock:
            raise forms.ValidationError("Этот вариант товара закончился.")

        if quantity > variant.stock:
            raise forms.ValidationError(f"Доступно только {variant.stock} шт.")

        cleaned_data["variant"] = variant

        return cleaned_data
