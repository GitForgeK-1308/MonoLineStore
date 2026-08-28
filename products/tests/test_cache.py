from django.core.cache import cache
from django.test import TestCase, override_settings

from products.cache import (
    CATEGORIES_CACHE_KEY,
    get_cached_categories,
)
from products.models import Category


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "products-cache-tests",
        }
    }
)
class CategoriesCacheTests(TestCase):
    def setUp(self):
        cache.clear()

        self.clothes = Category.objects.create(
            name="Одежда",
            slug="clothes-cache",
        )

        self.shoes = Category.objects.create(
            name="Обувь",
            slug="shoes-cache",
        )

        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_cache_miss_loads_categories_from_database(self):
        with self.assertNumQueries(1):
            categories = get_cached_categories()

        self.assertEqual(
            [category.name for category in categories],
            [
                "Обувь",
                "Одежда",
            ],
        )

        self.assertIsNotNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

    def test_cache_hit_does_not_query_database(self):
        get_cached_categories()

        with self.assertNumQueries(0):
            categories = get_cached_categories()

        self.assertEqual(
            len(categories),
            2,
        )

    def test_category_create_invalidates_cache(self):
        get_cached_categories()

        self.assertIsNotNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

        Category.objects.create(
            name="Аксессуары",
            slug="accessories-cache",
        )

        self.assertIsNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

    def test_category_update_invalidates_cache(self):
        get_cached_categories()

        self.assertIsNotNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

        self.clothes.name = "Мужская одежда"
        self.clothes.save()

        self.assertIsNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

    def test_category_delete_invalidates_cache(self):
        get_cached_categories()

        self.assertIsNotNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )

        self.shoes.delete()

        self.assertIsNone(
            cache.get(
                CATEGORIES_CACHE_KEY,
            )
        )
