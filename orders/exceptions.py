class CheckoutError(Exception):
    pass


class EmptyCartError(CheckoutError):
    pass


class CartItemUnavailableError(CheckoutError):
    pass


class InsufficientStockError(CheckoutError):
    pass
