from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "first_name",
            "phone",
            "email",
            "address",
            "comment",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "autocomplete": "given-name",
                    "placeholder": "Ваше имя",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "placeholder": "Телефон",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                    "placeholder": "Email",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "autocomplete": "street-address",
                    "placeholder": "Адрес доставки",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "placeholder": "Комментарий к заказу",
                    "rows": 4,
                }
            ),
        }
