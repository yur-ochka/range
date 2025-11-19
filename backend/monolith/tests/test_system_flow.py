import time
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Category, Product
from apps.cart.models import CartItem
from apps.order.models import Order
from apps.payment.models import PaymentTransaction


class SystemFlowTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='System Test Category')
        self.product = Product.objects.create(
            title='System Test Sneaker',
            description='Comfort runner',
            brand='SystemBrand',
            price=Decimal('120.00'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=25,
            in_stock=True,
        )
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.product_list_url = reverse('product-list')
        self.cart_add_url = reverse('cart-items-add')
        self.order_create_url = reverse('order-create-from-cart')
        self.payment_create_url = reverse('payment-create')
        self.payment_webhook_url = reverse('payment-webhook')
        self.guest_session_url = reverse('guest-session')

    def test_authenticated_checkout_flow(self):
        start = time.perf_counter()

        # 1. Register a new user
        email = 'systemtest@example.com'
        password = 'StrongPass123!'
        register_resp = self.client.post(
            self.register_url,
            {
                'email': email,
                'username': 'system_user',
                'password': password,
                'password_confirm': password,
                'first_name': 'System',
                'last_name': 'Tester',
            },
            format='json',
        )
        self.assertEqual(register_resp.status_code, status.HTTP_201_CREATED)

        # 2. Login to obtain tokens
        login_resp = self.client.post(
            self.login_url,
            {'email': email, 'password': password},
            format='json',
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access_token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 3. Browse catalog
        catalog_resp = self.client.get(self.product_list_url)
        self.assertEqual(catalog_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(catalog_resp.data['count'], 1)

        # 4. Add product to cart
        add_resp = self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 2},
            format='json',
        )
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)

        # 5. Create order from cart
        order_resp = self.client.post(
            self.order_create_url,
            {
                'shipping_address': '123 Test Street',
                'contact_email': email,
                'contact_phone': '+123456789',
                'contact_name': 'System Tester',
            },
            format='json',
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order_id = order_resp.data['id']
        self.assertEqual(CartItem.objects.count(), 0)

        # 6. Initiate payment
        payment_resp = self.client.post(
            self.payment_create_url,
            {'order_id': order_id},
            format='json',
        )
        self.assertEqual(payment_resp.status_code, status.HTTP_201_CREATED)
        payment_id = payment_resp.data['id']
        provider = payment_resp.data['provider']
        provider_id = payment_resp.data['provider_id']

        # 7. Simulate provider webhook success
        webhook_resp = self.client.post(
            self.payment_webhook_url,
            {
                'provider': provider,
                'provider_id': provider_id,
                'event': 'payment_succeeded',
            },
            format='json',
        )
        self.assertEqual(webhook_resp.status_code, status.HTTP_200_OK)

        # 8. Verify order status updated to PAID
        order_detail_url = reverse('order-detail', kwargs={'id': order_id})
        order_detail_resp = self.client.get(order_detail_url)
        self.assertEqual(order_detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(order_detail_resp.data['status'], Order.STATUS_PAID)

        payment = PaymentTransaction.objects.get(id=payment_id)
        self.assertEqual(payment.status, PaymentTransaction.STATUS_SUCCEEDED)

        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 5.0, f"System flow took too long ({elapsed:.2f}s)")

    def test_guest_checkout_payment_failure(self):
        contact_email = 'guestbuyer@example.com'

        guest_resp = self.client.post(self.guest_session_url)
        self.assertEqual(guest_resp.status_code, status.HTTP_200_OK)
        self.assertIn('session_key', guest_resp.data)

        add_resp = self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 1},
            format='json',
        )
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)

        order_resp = self.client.post(
            self.order_create_url,
            {
                'shipping_address': 'Guest Street 9',
                'contact_email': contact_email,
                'contact_phone': '+380987654321',
                'contact_name': 'Guest Buyer',
            },
            format='json',
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order_id = order_resp.data['id']
        self.assertEqual(CartItem.objects.count(), 0)

        payment_resp = self.client.post(
            self.payment_create_url,
            {'order_id': order_id},
            format='json',
        )
        self.assertEqual(payment_resp.status_code, status.HTTP_201_CREATED)
        payment_id = payment_resp.data['id']

        webhook_resp = self.client.post(
            self.payment_webhook_url,
            {
                'provider': payment_resp.data['provider'],
                'provider_id': payment_resp.data['provider_id'],
                'event': 'payment_failed',
            },
            format='json',
        )
        self.assertEqual(webhook_resp.status_code, status.HTTP_200_OK)

        payment = PaymentTransaction.objects.get(id=payment_id)
        self.assertEqual(payment.status, PaymentTransaction.STATUS_FAILED)

        lookup_url = reverse('order-lookup', kwargs={'id': order_id})
        lookup_resp = self.client.get(lookup_url, {'email': contact_email})
        self.assertEqual(lookup_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(lookup_resp.data['status'], Order.STATUS_CANCELLED)

    def test_refund_flow_after_success(self):
        email = 'refund@example.com'
        password = 'StrongPass123!'

        register_resp = self.client.post(
            self.register_url,
            {
                'email': email,
                'username': 'refund_user',
                'password': password,
                'password_confirm': password,
                'first_name': 'Refund',
                'last_name': 'Tester',
            },
            format='json',
        )
        self.assertEqual(register_resp.status_code, status.HTTP_201_CREATED)

        login_resp = self.client.post(
            self.login_url,
            {'email': email, 'password': password},
            format='json',
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_resp.data['access']}")

        add_resp = self.client.post(
            self.cart_add_url,
            {'product_id': str(self.product.id), 'quantity': 1},
            format='json',
        )
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)

        order_resp = self.client.post(
            self.order_create_url,
            {
                'shipping_address': 'Refund Ave 1',
                'contact_email': email,
                'contact_phone': '+123123123',
                'contact_name': 'Refund Tester',
            },
            format='json',
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order_id = order_resp.data['id']

        payment_resp = self.client.post(
            self.payment_create_url,
            {'order_id': order_id},
            format='json',
        )
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
        self.assertEqual(webhook_resp.status_code, status.HTTP_200_OK)

        refund_url = reverse('payment-refund', kwargs={'payment_id': payment_id})
        refund_resp = self.client.post(refund_url, {'amount': '60.00'}, format='json')
        self.assertEqual(refund_resp.status_code, status.HTTP_201_CREATED)

        refund_detail_url = reverse('refund-detail', kwargs={'refund_id': refund_resp.data['id']})
        refund_detail_resp = self.client.get(refund_detail_url)
        self.assertEqual(refund_detail_resp.status_code, status.HTTP_200_OK)

        payment = PaymentTransaction.objects.get(id=payment_id)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentTransaction.STATUS_PARTIALLY_REFUNDED)
        self.assertEqual(str(payment.refunded_amount), '60.00')

        order_detail_url = reverse('order-detail', kwargs={'id': order_id})
        order_detail_resp = self.client.get(order_detail_url)
        self.assertEqual(order_detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(order_detail_resp.data['status'], Order.STATUS_PAID)
