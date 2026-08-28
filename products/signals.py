from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache import invalidate_categories_cache
from .models import Category


@receiver(
    post_save,
    sender=Category,
)
@receiver(
    post_delete,
    sender=Category,
)
def invalidate_category_cache(**kwargs):
    invalidate_categories_cache()
