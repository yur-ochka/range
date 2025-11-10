from django.contrib import admin
from .models import PaymentTransaction, Refund


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'amount', 'currency', 'status', 'provider', 'provider_id', 'created_at')
    list_filter = ('status', 'provider', 'currency')
    search_fields = ('provider_id',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'currency', 'status', 'provider_refund_id', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('provider_refund_id',)
