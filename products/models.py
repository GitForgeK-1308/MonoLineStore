from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Gender(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Пол"
        verbose_name_plural = "Пол"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class ProductType(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="types",
        verbose_name="Категория",
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
        verbose_name="Тип товара",
    )
    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
        verbose_name="Пол",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        verbose_name="Изображение",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        verbose_name="Цена",
    )
    discount = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        verbose_name="Скидка в %",
    )
    is_popular = models.BooleanField(
        default=False,
        verbose_name="Популярный товар",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    @property
    def in_stock(self):
        return any(variant.stock > 0 for variant in self.variants.all())

    @property
    def total_stock(self):
        return sum(variant.stock for variant in self.variants.all())

    @property
    def discounted_price(self):
        if not self.discount:
            return self.price

        multiplier = Decimal(100 - self.discount) / Decimal("100")

        return (self.price * multiplier).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def clean(self):
        super().clean()

        if (
            self.product_type_id
            and self.category_id
            and self.product_type.category_id != self.category_id
        ):
            raise ValidationError(
                {
                    "product_type": (
                        "Тип товара должен принадлежать выбранной категории."
                    )
                }
            )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=Decimal("0.01")),
                name="product_price_gte_001",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    discount__gte=0,
                    discount__lte=100,
                ),
                name="product_discount_between_0_and_100",
            ),
        ]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    class Size(models.TextChoices):
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"

    class Color(models.TextChoices):
        WHITE = "white", "Белый"
        BLACK = "black", "Черный"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Товар",
    )
    color = models.CharField(
        max_length=10,
        choices=Color.choices,
        verbose_name="Цвет",
    )
    size = models.CharField(
        max_length=10,
        choices=Size.choices,
        verbose_name="Размер",
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Остаток",
    )

    @property
    def in_stock(self):
        return self.stock > 0

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товара"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "color",
                    "size",
                ],
                name="unique_product_color_size",
            )
        ]

    def __str__(self):
        return f"{self.product.name} / {self.get_color_display()} / {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    image = models.ImageField(
        upload_to="products/gallery/",
        verbose_name="Изображение",
    )
    alt_text = models.CharField(
        max_length=100,
        verbose_name="Альтернативный текст",
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self):
        return f"Изображение для {self.product.name}"
