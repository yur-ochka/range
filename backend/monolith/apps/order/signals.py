from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order
from .services import send_order_created_email, send_order_status_email


@receiver(pre_save, sender=Order)
def stash_previous_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    try:
        previous = sender.objects.get(pk=instance.pk).status
    except sender.DoesNotExist:
        previous = None
    instance._previous_status = previous


@receiver(post_save, sender=Order)
def notify_status_change(sender, instance, created, **kwargs):
    if created:
        send_order_created_email(instance)
        return

    previous_status = getattr(instance, '_previous_status', None)
    if previous_status and previous_status != instance.status:
        send_order_status_email(instance, previous_status)
