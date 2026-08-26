from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PROCESSING = "processing", "В обработке"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    ALLOWED_STATUS_TRANSITIONS = {
        Status.NEW: {
            Status.PROCESSING,
            Status.CANCELLED,
        },
        Status.PROCESSING: {
            Status.COMPLETED,
            Status.CANCELLED,
        },
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Пользователь",
    )

    first_name = models.CharField(
        "Имя",
        max_length=100,
    )

    phone = models.CharField(
        "Телефон",
        max_length=30,
    )

    email = models.EmailField(
        "Email",
    )

    address = models.CharField(
        "Адрес доставки",
        max_length=255,
    )

    comment = models.TextField(
        "Комментарий",
        blank=True,
    )

    total_price = models.DecimalField(
        "Итоговая сумма",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            )
        ],
    )

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    total_price__gte=Decimal("0.00"),
                ),
                name="order_total_price_gte_000",
            ),
        ]

    def can_transition_to(self, new_status):
        if new_status == self.status:
            return True

        return new_status in self.ALLOWED_STATUS_TRANSITIONS.get(
            self.status,
            set(),
        )

    def transition_to(self, new_status):
        if new_status not in self.Status.values:
            raise ValidationError(
                {
                    "status": "Неизвестный статус заказа.",
                }
            )

        if not self.can_transition_to(new_status):
            raise ValidationError(
                {
                    "status": (
                        f"Нельзя изменить статус "
                        f"с «{self.get_status_display()}» "
                        f"на «{self.Status(new_status).label}»."
                    ),
                }
            )

        if new_status == self.status:
            return

        self.status = new_status
        self.save(
            update_fields=(
                "status",
                "updated_at",
            )
        )

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="Вариант товара",
    )

    product_name = models.CharField(
        "Название товара",
        max_length=150,
    )

    product_slug = models.SlugField(
        "Slug товара",
        max_length=150,
    )

    color = models.CharField(
        "Цвет",
        max_length=50,
    )

    size = models.CharField(
        "Размер",
        max_length=50,
    )

    price = models.DecimalField(
        "Цена за штуку",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            )
        ],
    )

    quantity = models.PositiveIntegerField(
        "Количество",
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    price__gte=Decimal("0.00"),
                ),
                name="order_item_price_gte_000",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity__gte=1,
                ),
                name="order_item_quantity_gte_1",
            ),
        ]

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product_name
