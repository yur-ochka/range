import uuid
from django.db import models
from django.conf import settings
from django.apps import apps


class PaymentTransaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCEEDED = 'succeeded'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCEEDED, 'Succeeded'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_PARTIALLY_REFUNDED, 'Partially Refunded'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # use lazy resolve of Order to avoid hard-coded model path string issues
    order = models.ForeignKey('order.Order', null=True, blank=True, on_delete=models.SET_NULL, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider = models.CharField(max_length=50, blank=True, null=True)
    provider_id = models.CharField(max_length=128, blank=True, null=True)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment({self.id}) amount={self.amount} status={self.status}"

    def recalculate_refund_status(self):
        """Recalculate refunded amount and set status accordingly."""
        from django.db.models import Sum
        total = self.refunds.filter(status=Refund.STATUS_SUCCEEDED).aggregate(s=Sum('amount'))['s'] or 0
        self.refunded_amount = total
        if total <= 0:
            if self.status in (self.STATUS_REFUNDED, self.STATUS_PARTIALLY_REFUNDED):
                self.status = self.STATUS_SUCCEEDED
        elif total < self.amount:
            self.status = self.STATUS_PARTIALLY_REFUNDED
        else:
            self.status = self.STATUS_REFUNDED
        self.save(update_fields=['refunded_amount', 'status', 'updated_at'])


class Refund(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCEEDED = 'succeeded'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCEEDED, 'Succeeded'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(PaymentTransaction, related_name='refunds', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider = models.CharField(max_length=50, blank=True, null=True)
    provider_refund_id = models.CharField(max_length=128, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund({self.id}) payment={self.payment_id} amount={self.amount} status={self.status}"
