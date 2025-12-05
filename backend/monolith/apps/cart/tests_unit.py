from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.catalog.models import Category, Product
from apps.cart.models import Cart, CartItem


class CartModelUnitTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='unit-cat')
        self.product = Product.objects.create(
            title='Unit Product',
            description='For unit tests',
            brand='UnitBrand',
            price=Decimal('10.00'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=10,
            in_stock=True,
        )

    def test_cartitem_subtotal(self):
        cart = Cart.objects.create(session_key='s-123')
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=3,
            unit_price=Decimal('10.50'),
        )
        self.assertEqual(item.subtotal(), Decimal('31.50'))

    def test_cart_total_with_multiple_items(self):
        cart = Cart.objects.create(session_key='s-456')
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
            unit_price=Decimal('5.00'),
        )
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
            unit_price=Decimal('12.30'),
        )
        # 2*5.00 + 1*12.30 = 22.30
        self.assertEqual(cart.total(), Decimal('22.30'))

    def test_cart_total_empty_returns_zero(self):
        cart = Cart.objects.create(session_key='empty-session')
        # empty cart.total() uses sum([]) which returns 0
        self.assertEqual(cart.total(), 0)

    def test_cart_str_representation_session(self):
        cart = Cart.objects.create(session_key='session-x')
        s = str(cart)
        self.assertIn('session', s)

    def test_cart_str_representation_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='tu',
            email='tu@example.com',
            password='pass',
            first_name='T',
            last_name='U',
        )
        cart = Cart.objects.create(user=user)
        s = str(cart)
        # should not contain session text when user is present
        self.assertNotIn('session', s)
        self.assertIn('Cart(', s)
