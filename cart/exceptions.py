class CartError(Exception):
    pass


class InvalidCartQuantityError(CartError):
    pass


class InsufficientStockError(CartError):
    pass
