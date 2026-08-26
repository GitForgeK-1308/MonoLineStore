from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import QuerySet

from .models import Product


def search_products(
    queryset: QuerySet[Product],
    query: str,
) -> QuerySet[Product]:
    query = query.strip()

    if not query:
        return queryset

    if query.isdigit():
        return queryset.filter(pk=int(query))

    search_vector = (
        SearchVector(
            "name",
            weight="A",
            config="simple",
        )
        + SearchVector(
            "description",
            weight="B",
            config="simple",
        )
    )

    search_query = SearchQuery(
        query,
        search_type="websearch",
        config="simple",
    )

    return (
        queryset
        .annotate(
            search_rank=SearchRank(
                search_vector,
                search_query,
            )
        )
        .filter(search_rank__gt=0)
        .order_by(
            "-search_rank",
            "-created_at",
        )
    )