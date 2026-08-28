from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_order_created_email(order_id):
    order = Order.objects.prefetch_related("items").get(pk=order_id)

    context = {
        "order": order,
    }

    subject = f"MONO LINE — заказ №{order.pk} оформлен"

    text_body = render_to_string(
        "orders/email/order_created.txt",
        context,
    )

    html_body = render_to_string(
        "orders/email/order_created.html",
        context,
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )

    message.attach_alternative(
        html_body,
        "text/html",
    )

    return message.send()
