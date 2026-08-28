from django.core.cache import cache

from .models import Category


CATEGORIES_CACHE_KEY = "products:categories"
CATEGORIES_CACHE_TIMEOUT = 300


def get_cached_categories():
    categories = cache.get(
        CATEGORIES_CACHE_KEY,
    )

    if categories is None:
        categories = list(
            Category.objects.order_by(
                "name",
            )
        )

        cache.set(
            CATEGORIES_CACHE_KEY,
            categories,
            timeout=CATEGORIES_CACHE_TIMEOUT,
        )

    return categories


def invalidate_categories_cache():
    cache.delete(
        CATEGORIES_CACHE_KEY,
    )
