from django.conf import settings
from django.core.mail import send_mail

from .models import Order


def _order_recipient(order):
    return order.contact_email or (order.user.email if order.user else None)


def _order_greeting(order):
    if order.contact_name:
        return order.contact_name
    if order.user and order.user.first_name:
        return order.user.first_name
    return 'Customer'


def _status_display(status_value):
    return dict(Order.STATUS_CHOICES).get(status_value, status_value)


def send_order_created_email(order):
    recipient = _order_recipient(order)
    if not recipient:
        return

    subject = f"Order {order.id} confirmation"
    message = (
        f"Hello {_order_greeting(order)},\n\n"
        f"We have received your order {order.id}.\n"
        f"Current status: {order.get_status_display()}.\n\n"
        "We will notify you as soon as it ships.\n\n"
        "Thank you for shopping with us."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)


def send_order_status_email(order, previous_status):
    recipient = _order_recipient(order)
    if not recipient:
        return

    subject = f"Order {order.id} status update"
    message = (
        f"Hello {_order_greeting(order)},\n\n"
        f"Your order {order.id} status changed from {_status_display(previous_status)} to {order.get_status_display()}.\n\n"
        "You can continue tracking your order with the provided order number.\n\n"
        "Thank you for shopping with us."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
