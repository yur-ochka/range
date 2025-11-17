from decimal import Decimal

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cart.models import Cart
from apps.catalog.models import Category, Product
from apps.order.models import Order, OrderItem
from apps.user.models import User


class OrderGuestCheckoutTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Gadgets')
        self.product = Product.objects.create(
            title='Smart Watch',
            description='Tracks your activity',
            brand='TrackIt',
            price=Decimal('149.99'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=10,
            in_stock=True,
        )
        self.cart_add_url = reverse('cart-items-add')
        self.order_create_url = reverse('order-create-from-cart')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_guest_checkout_uses_cart_and_sends_email(self):
        add_response = self.client.post(
            self.cart_add_url,
            {'product_id': self.product.id, 'quantity': 2},
            format='json',
        )
        self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)

        payload = {
            'shipping_address': 'Kyiv, Ukraine',
            'contact_email': 'guest@example.com',
            'contact_phone': '+380501112233',
            'contact_name': 'Guest Shopper',
        }
        response = self.client.post(self.order_create_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.contact_email, payload['contact_email'])
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal('299.98'))
        self.assertEqual(len(mail.outbox), 1)

        session_key = self.client.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        self.assertIsNotNone(cart)
        self.assertFalse(cart.items.exists())

        lookup_url = reverse('order-lookup', kwargs={'id': order.id})
        lookup_response = self.client.get(lookup_url, {'email': payload['contact_email']})
        self.assertEqual(lookup_response.status_code, status.HTTP_200_OK)
        self.assertEqual(lookup_response.data['id'], str(order.id))


class OrderAdminTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email='admin@example.com',
            username='adminuser',
            password='StrongPass123!',
            first_name='Admin',
            last_name='User',
        )
        self.staff.is_staff = True
        self.staff.save(update_fields=['is_staff'])
        self.category = Category.objects.create(title='Appliances')
        self.product = Product.objects.create(
            title='Blender',
            description='Kitchen blender',
            brand='MixPro',
            price=Decimal('89.50'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=5,
            in_stock=True,
        )
        self.order = Order.objects.create(
            shipping_address='Lviv, Ukraine',
            contact_email='buyer@example.com',
            total_amount=self.product.price,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
        )
        self.status_url = reverse('order-status-update', kwargs={'id': self.order.id})
        self.admin_list_url = reverse('order-admin-list')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_staff_can_update_status_and_trigger_email(self):
        self.client.force_authenticate(user=self.staff)
        mail.outbox.clear()
        response = self.client.patch(self.status_url, {'status': Order.STATUS_SHIPPED}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_SHIPPED)
        self.assertEqual(len(mail.outbox), 1)

    def test_non_staff_cannot_access_admin_list(self):
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)