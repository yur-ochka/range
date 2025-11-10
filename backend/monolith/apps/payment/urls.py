from django.urls import path
from .views import CreatePaymentView, PaymentDetailView, WebhookView, CreateRefundView, RefundDetailView

urlpatterns = [
    path('create/', CreatePaymentView.as_view(), name='payment-create'),
    path('<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('webhook/', WebhookView.as_view(), name='payment-webhook'),
    path('<uuid:payment_id>/refund/', CreateRefundView.as_view(), name='payment-refund'),
    path('refunds/<uuid:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),
]
