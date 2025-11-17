from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .serializers import PaymentTransactionSerializer, PaymentCreateSerializer
from .models import PaymentTransaction
from . import services


def _set_order_status(transaction, status_value):
    order = getattr(transaction, 'order', None)
    if order and status_value:
        if order.status != status_value:
            order.status = status_value
            order.save(update_fields=['status', 'updated_at'])


class CreatePaymentView(APIView):
    """Create a payment transaction (payment intent) for an order."""

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data['order_id']

        # import here to avoid circular import at module import time
        from apps.order.models import Order

        order = get_object_or_404(Order, id=order_id)

        # create a local PaymentTransaction record
        amount = getattr(order, 'total_amount', None) or order.calculate_total()
        tx = PaymentTransaction.objects.create(
            order=order,
            user=order.user,
            amount=amount,
            currency='USD',
            status=PaymentTransaction.STATUS_PENDING,
        )

        # Basic idempotency key (order + local payment id) to avoid duplicate Stripe intents on retries
        idem_key = f"pi_{order.id}_{tx.id}"
        intent = services.create_intent(
            amount=float(amount),
            currency='USD',
            metadata={'order_id': str(order.id), 'payment_id': str(tx.id)},
            idempotency_key=idem_key,
        )

        tx.provider = intent.get('provider')
        tx.provider_id = intent.get('provider_id')
        tx.metadata = intent.get('metadata')
        tx.save()

        out = PaymentTransactionSerializer(tx)
        data = out.data
        if 'client_secret' in intent:
            data['client_secret'] = intent['client_secret']
        return Response(data, status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    def get(self, request, payment_id):
        tx = get_object_or_404(PaymentTransaction, id=payment_id)
        return Response(PaymentTransactionSerializer(tx).data)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """Webhook endpoint for Stripe (or dummy) payment events.

    When Stripe is configured, validates the signature and processes events
    such as payment_intent.succeeded / payment_intent.payment_failed /
    charge.refunded.
    For the dummy provider, we fallback to simple JSON structure as before.
    """

    permission_classes = []  # public endpoint (secured via signature for Stripe)

    def post(self, request):
        # Stripe integration path when keys are present
        if getattr(settings, 'STRIPE_API_KEY', None) and getattr(settings, 'STRIPE_WEBHOOK_SECRET', None):
            sig = request.META.get('HTTP_STRIPE_SIGNATURE')
            if not sig:
                return Response({'detail': 'missing Stripe-Signature header'}, status=status.HTTP_400_BAD_REQUEST)
            import json
            from . import services
            try:
                event = services.construct_stripe_event(request.body, sig)
            except Exception as e:  # signature or JSON error
                return Response({'detail': f'webhook error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

            event_type = event.get('type')
            data_object = event.get('data', {}).get('object', {})

            # Handle payment intents
            if event_type in ('payment_intent.succeeded', 'payment_intent.payment_failed'):
                pi_id = data_object.get('id')
                tx = PaymentTransaction.objects.filter(provider='stripe', provider_id=pi_id).first()
                if tx:
                    if event_type == 'payment_intent.succeeded':
                        tx.status = PaymentTransaction.STATUS_SUCCEEDED
                        tx.save()
                        _set_order_status(tx, tx.order.STATUS_PAID if tx.order else None)
                    else:
                        tx.status = PaymentTransaction.STATUS_FAILED
                        tx.save()
                        _set_order_status(tx, tx.order.STATUS_CANCELLED if tx.order else None)
            # Handle charge refunded events (Stripe might send charge.refunded)
            elif event_type == 'charge.refunded':
                # If refund happened from dashboard, update local payment status/amount
                pi_id = data_object.get('payment_intent')
                amount_refunded_minor = data_object.get('amount_refunded') or 0
                tx = PaymentTransaction.objects.filter(provider='stripe', provider_id=pi_id).first()
                if tx:
                    # Convert minor units to major
                    refunded_major = (amount_refunded_minor or 0) / 100.0
                    tx.refunded_amount = refunded_major
                    if refunded_major <= 0:
                        pass
                    elif refunded_major < float(tx.amount):
                        tx.status = PaymentTransaction.STATUS_PARTIALLY_REFUNDED
                        tx.save()
                        _set_order_status(tx, tx.order.STATUS_PENDING if tx.order else None)
                    else:
                        tx.status = PaymentTransaction.STATUS_REFUNDED
                        tx.save()
                        _set_order_status(tx, tx.order.STATUS_CANCELLED if tx.order else None)
            return Response({'received': True})

        # Dummy fallback path
        payload = request.data or {}
        provider = payload.get('provider')
        provider_id = payload.get('provider_id')
        event = payload.get('event')
        if not provider or not provider_id or not event:
            return Response({'detail': 'invalid webhook payload'}, status=status.HTTP_400_BAD_REQUEST)
        tx = PaymentTransaction.objects.filter(provider=provider, provider_id=provider_id).first()
        if not tx:
            return Response({'detail': 'unknown transaction'}, status=status.HTTP_404_NOT_FOUND)
        if event == 'payment_succeeded':
            tx.status = PaymentTransaction.STATUS_SUCCEEDED
            tx.save()
            _set_order_status(tx, tx.order.STATUS_PAID if tx.order else None)
        elif event == 'payment_failed':
            tx.status = PaymentTransaction.STATUS_FAILED
            tx.save()
            _set_order_status(tx, tx.order.STATUS_CANCELLED if tx.order else None)
        return Response({'ok': True})


class CreateRefundView(APIView):
    """Create a refund for a given payment."""

    def post(self, request, payment_id):
        from .models import Refund
        from .serializers import RefundSerializer, RefundCreateSerializer
        # bind serializer model to avoid circular-import at module load time
        RefundSerializer.Meta.model = Refund

        payment = get_object_or_404(PaymentTransaction, id=payment_id)

        serializer = RefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        # ensure refund amount does not exceed payment amount (basic check)
        if amount > payment.amount:
            return Response({'detail': 'refund amount exceeds payment amount'}, status=status.HTTP_400_BAD_REQUEST)

        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            currency=payment.currency,
            status=Refund.STATUS_PENDING,
        )

        # call provider refund
        if not payment.provider or not payment.provider_id:
            # nothing to call; mark failed
            refund.status = Refund.STATUS_FAILED
            refund.save()
            return Response(RefundSerializer(refund).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        idem_key = f"rf_{payment.id}_{refund.id}_{amount}"
        result = services.refund_payment(
            payment.provider,
            payment.provider_id,
            float(amount),
            metadata={'payment_id': str(payment.id), 'refund_id': str(refund.id)},
            idempotency_key=idem_key,
        )

        refund.provider = result.get('provider')
        refund.provider_refund_id = result.get('provider_refund_id')
        refund.metadata = result.get('metadata')
        refund.status = Refund.STATUS_SUCCEEDED if result.get('status') == 'succeeded' else Refund.STATUS_FAILED
        refund.save()

        if refund.status == Refund.STATUS_SUCCEEDED:
            payment.recalculate_refund_status()

        out = RefundSerializer(refund)
        return Response(out.data, status=status.HTTP_201_CREATED)


class RefundDetailView(APIView):
    def get(self, request, refund_id):
        from .models import Refund
        from .serializers import RefundSerializer
        RefundSerializer.Meta.model = Refund

        refund = get_object_or_404(Refund, id=refund_id)
        return Response(RefundSerializer(refund).data)
