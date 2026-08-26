from django.contrib.sessions.middleware import (
    SessionMiddleware,
)
from django.test import RequestFactory, TestCase

from cart.context_processors import cart_summary
from cart.services import CART_SESSION_KEY


class CartContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def get_request(self):
        request = self.factory.get("/")

        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)

        request.session.save()

        return request

    def test_empty_cart_quantity_is_zero(self):
        request = self.get_request()

        context = cart_summary(request)

        self.assertEqual(
            context["cart_quantity"],
            0,
        )

    def test_cart_quantity_contains_total_number_of_items(self):
        request = self.get_request()

        request.session[CART_SESSION_KEY] = {
            "1": 2,
            "2": 3,
        }

        context = cart_summary(request)

        self.assertEqual(
            context["cart_quantity"],
            5,
        )
