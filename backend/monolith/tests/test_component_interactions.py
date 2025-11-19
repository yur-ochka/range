import uuid
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Category, Product
from apps.cart.models import CartItem
from apps.order.models import Order
from apps.payment.models import PaymentTransaction


class ComponentInteractionTests(APITestCase):
    """Focused tests that validate interaction between modules via public APIs."""

    def setUp(self):
        self.category = Category.objects.create(title='Component Category')
        self.product = Product.objects.create(
            title='Component Shoe',
            description='Cross-module test product',
            brand='CompBrand',
            price=Decimal('75.00'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=15,
            in_stock=True,
        )
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.cart_detail_url = reverse('cart-detail')
        self.cart_add_url = reverse('cart-items-add')
        self.order_create_url = reverse('order-create-from-cart')
        self.order_lookup_name = 'order-lookup'
        self.payment_create_url = reverse('payment-create')
        self.payment_webhook_url = reverse('payment-webhook')
        self.payment_detail_name = 'payment-detail'
        self.guest_session_url = reverse('guest-session')

    # Helpers -----------------------------------------------------------------
    def _register_and_authenticate(self, email=None, password='StrongPass123!'):
        email = email or f"component_{uuid.uuid4().hex[:8]}@example.com"
        username = f"user_{uuid.uuid4().hex[:8]}"
        payload = {
            'email': email,
            'username': username,
            'password': password,
            'password_confirm': password,
            'first_name': 'Component',
            'last_name': 'Tester',
        }
        register_resp = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(register_resp.status_code, status.HTTP_201_CREATED)

        login_resp = self.client.post(
            self.login_url,
            {'email': email, 'password': password},
            format='json',
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return email

    def _log_response(self, label, response):
        payload = getattr(response, 'data', None)
        print(f"\n[{self._testMethodName}] {label}: status={response.status_code}\n{payload}\n")

    # Tests --------------------------------------------------------------------
    def test_cart_to_order_interaction_returns_consistent_payloads(self):
        email = self._register_and_authenticate()

        add_resp = self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 3},
            format='json',
        )
        self._log_response('cart-add', add_resp)
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)
        for key in ('id', 'product_id', 'quantity', 'unit_price'):
            self.assertIn(key, add_resp.data)

        cart_resp = self.client.get(self.cart_detail_url)
        self._log_response('cart-detail', cart_resp)
        self.assertEqual(cart_resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cart_resp.data['user'])
        self.assertEqual(len(cart_resp.data['items']), 1)
        self.assertEqual(cart_resp.data['items'][0]['quantity'], 3)
        self.assertGreater(Decimal(str(cart_resp.data['total'])), Decimal('0'))

        order_payload = {
            'shipping_address': 'Component Street 1',
            'contact_email': email,
            'contact_phone': '+111111111',
            'contact_name': 'Component Tester',
        }
        order_resp = self.client.post(self.order_create_url, order_payload, format='json')
        self._log_response('order-create', order_resp)
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(order_resp.data['items']), 1)
        self.assertEqual(order_resp.data['items'][0]['quantity'], 3)
        self.assertEqual(CartItem.objects.count(), 0)
        order = Order.objects.get(id=order_resp.data['id'])
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 3)

    def test_payment_webhook_updates_order_and_payment_statuses(self):
        email = self._register_and_authenticate()

        self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 1},
            format='json',
        )
        order_resp = self.client.post(
            self.order_create_url,
            {
                'shipping_address': 'Payment Street 2',
                'contact_email': email,
                'contact_phone': '+222222222',
                'contact_name': 'Payment Tester',
            },
            format='json',
        )
        self._log_response('order-create', order_resp)
        order_id = order_resp.data['id']

        payment_resp = self.client.post(
            self.payment_create_url,
            {'order_id': order_id},
            format='json',
        )
        self._log_response('payment-create', payment_resp)
        self.assertEqual(payment_resp.status_code, status.HTTP_201_CREATED)
        payment_id = payment_resp.data['id']

        webhook_resp = self.client.post(
            self.payment_webhook_url,
            {
                'provider': payment_resp.data['provider'],
                'provider_id': payment_resp.data['provider_id'],
                'event': 'payment_succeeded',
            },
            format='json',
        )
        self._log_response('payment-webhook', webhook_resp)
        self.assertEqual(webhook_resp.status_code, status.HTTP_200_OK)

        order_detail = self.client.get(reverse('order-detail', kwargs={'id': order_id}))
        self._log_response('order-detail', order_detail)
        self.assertEqual(order_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(order_detail.data['status'], Order.STATUS_PAID)

        payment_detail = self.client.get(reverse(self.payment_detail_name, kwargs={'payment_id': payment_id}))
        self._log_response('payment-detail', payment_detail)
        self.assertEqual(payment_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(payment_detail.data['status'], PaymentTransaction.STATUS_SUCCEEDED)

    def test_guest_checkout_lookup_api_flow(self):
        contact_email = 'component-guest@example.com'

        guest_resp = self.client.post(self.guest_session_url)
        self._log_response('guest-session', guest_resp)
        self.assertEqual(guest_resp.status_code, status.HTTP_200_OK)
        self.assertIn('session_key', guest_resp.data)

        self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 2},
            format='json',
        )

        order_resp = self.client.post(
            self.order_create_url,
            {
                'shipping_address': 'Guest Ave 3',
                'contact_email': contact_email,
                'contact_phone': '+333333333',
                'contact_name': 'Guest Component',
            },
            format='json',
        )
        self._log_response('order-create', order_resp)
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order_id = order_resp.data['id']

        lookup_url = reverse(self.order_lookup_name, kwargs={'id': order_id})
        bad_lookup = self.client.get(lookup_url, {'email': 'wrong@example.com'})
        self._log_response('order-lookup-bad', bad_lookup)
        self.assertEqual(bad_lookup.status_code, status.HTTP_404_NOT_FOUND)

        good_lookup = self.client.get(lookup_url, {'email': contact_email})
        self._log_response('order-lookup-good', good_lookup)
        self.assertEqual(good_lookup.status_code, status.HTTP_200_OK)
        self.assertEqual(good_lookup.data['id'], order_id)
        self.assertEqual(len(good_lookup.data['items']), 1)