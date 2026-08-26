from .services import SessionCart


def cart_summary(request):
    return {
        "cart_quantity": len(SessionCart(request)),
    }
