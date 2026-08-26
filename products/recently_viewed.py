from .models import Product

VIEWED_PRODUCTS_SESSION_KEY = "viewed_products"
VIEWED_PRODUCTS_LIMIT = 4


def add_viewed_product(request, product_id):
    viewed_product_ids = request.session.get(
        VIEWED_PRODUCTS_SESSION_KEY,
        [],
    )

    product_id = int(product_id)

    if product_id in viewed_product_ids:
        viewed_product_ids.remove(product_id)

    viewed_product_ids.insert(0, product_id)

    request.session[VIEWED_PRODUCTS_SESSION_KEY] = viewed_product_ids[
        :VIEWED_PRODUCTS_LIMIT
    ]
    request.session.modified = True


def get_viewed_products(
    request,
    *,
    exclude_product_id=None,
):
    viewed_product_ids = request.session.get(
        VIEWED_PRODUCTS_SESSION_KEY,
        [],
    )

    if exclude_product_id is not None:
        exclude_product_id = int(exclude_product_id)

        viewed_product_ids = [
            product_id
            for product_id in viewed_product_ids
            if product_id != exclude_product_id
        ]

    products = Product.objects.filter(
        id__in=viewed_product_ids,
    )

    products_by_id = {product.id: product for product in products}

    return [
        products_by_id[product_id]
        for product_id in viewed_product_ids
        if product_id in products_by_id
    ]
