from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_password_reset_email(
    subject,
    body,
    from_email,
    to_email,
    html_body=None,
):
    message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[to_email],
    )

    if html_body:
        message.attach_alternative(
            html_body,
            "text/html",
        )

    return message.send()
