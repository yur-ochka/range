from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentWebhookTests(APITestCase):
    def setUp(self):
        self.webhook_url = reverse('payment-webhook')

    def test_webhook_missing_fields_returns_400(self):
        # No payload -> invalid
        resp = self.client.post(self.webhook_url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_unknown_transaction_returns_404(self):
        payload = {'provider': 'dummy', 'provider_id': 'nonexistent', 'event': 'payment_succeeded'}
        resp = self.client.post(self.webhook_url, payload, format='json')
        # When transaction is unknown, endpoint returns 404
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
