"""
Payment provider service: Stripe when configured, otherwise a local dummy.

This module exposes a stable interface for the views:
 - create_intent(amount, currency, metadata)
 - confirm_payment(provider, provider_id)
 - refund_payment(provider, provider_id, amount, metadata)
 - construct_stripe_event(payload, sig_header)  # used by webhook view
"""
import uuid
from django.conf import settings

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover - optional
    stripe = None


def _stripe_enabled():
    return bool(getattr(settings, 'STRIPE_API_KEY', None)) and stripe is not None


def _to_minor_units(amount):
    # amount may be Decimal; convert to int smallest currency unit
    return int(round(float(amount) * 100))


def create_intent(amount, currency='USD', metadata=None, idempotency_key=None):
    """Create a payment intent either on Stripe (if configured) or locally.

    Returns a dict with provider, provider_id and (optional) client_secret.
    """
    metadata = metadata or {}
    if _stripe_enabled():
        stripe.api_key = settings.STRIPE_API_KEY
        minor = _to_minor_units(amount)
        pi = stripe.PaymentIntent.create(
            amount=minor,
            currency=currency.lower(),
            metadata=metadata,
            automatic_payment_methods={"enabled": True},
            idempotency_key=idempotency_key,
        )
        return {
            'provider': 'stripe',
            'provider_id': pi.id,
            'client_secret': getattr(pi, 'client_secret', None),
            'metadata': dict(getattr(pi, 'metadata', {}) or {}),
        }

    # Fallback dummy provider
    provider_id = str(uuid.uuid4())
    return {
        'provider': 'local_dummy',
        'provider_id': provider_id,
        'client_secret': f'secret_{provider_id}',
        'metadata': metadata,
    }


def confirm_payment(provider, provider_id):
    """Confirm a payment if needed.

    For Stripe with PaymentIntents, confirmation typically happens client-side.
    We return succeeded for compatibility or could query the PI if desired.
    """
    if provider == 'stripe' and _stripe_enabled():
        # Optionally retrieve the PI to check status
        try:
            stripe.api_key = settings.STRIPE_API_KEY
            pi = stripe.PaymentIntent.retrieve(provider_id)
            status = 'succeeded' if getattr(pi, 'status', '') == 'succeeded' else 'pending'
            return {'status': status, 'provider': provider, 'provider_id': provider_id}
        except Exception:
            return {'status': 'failed', 'provider': provider, 'provider_id': provider_id}

    # Dummy/default behavior
    return {'status': 'succeeded', 'provider': provider, 'provider_id': provider_id}


def refund_payment(provider, provider_id, amount, metadata=None, idempotency_key=None):
    """Issue a refund via Stripe when enabled, otherwise dummy success.

    Returns a dict with provider, provider_refund_id and status.
    """
    metadata = metadata or {}
    if provider == 'stripe' and _stripe_enabled():
        try:
            stripe.api_key = settings.STRIPE_API_KEY
            r = stripe.Refund.create(payment_intent=provider_id, amount=_to_minor_units(amount), metadata=metadata, idempotency_key=idempotency_key)
            status = 'succeeded' if getattr(r, 'status', '') == 'succeeded' else 'failed'
            return {
                'status': status,
                'provider': 'stripe',
                'provider_refund_id': r.id,
                'metadata': dict(getattr(r, 'metadata', {}) or {}),
            }
        except Exception:
            return {'status': 'failed', 'provider': 'stripe', 'provider_refund_id': None, 'metadata': metadata}

    # Dummy fallback
    provider_refund_id = str(uuid.uuid4())
    return {
        'status': 'succeeded',
        'provider': provider,
        'provider_refund_id': provider_refund_id,
        'metadata': metadata,
    }


def construct_stripe_event(payload: bytes, sig_header: str):
    """Verify and construct a Stripe event using the webhook secret.

    Returns the event object or raises Exception on failure.
    """
    if not _stripe_enabled() or not getattr(settings, 'STRIPE_WEBHOOK_SECRET', None):
        raise RuntimeError('Stripe webhook not configured')
    stripe.api_key = settings.STRIPE_API_KEY
    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
