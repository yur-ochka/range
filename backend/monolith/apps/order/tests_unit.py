from decimal import Decimal

from django.test import TestCase

from apps.catalog.models import Category, Product
from apps.order.models import Order, OrderItem


class OrderModelUnitTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(title='order-cat')
        self.p = Product.objects.create(
            title='OP',
            description='d',
            brand='B',
            price=Decimal('20.00'),
            category=self.cat,
            rating=Decimal('0.00'),
            stock_quantity=5,
            in_stock=True,
        )

    def test_order_item_subtotal_and_order_total(self):
        order = Order.objects.create()
        oi1 = OrderItem.objects.create(order=order, product=self.p, quantity=2, unit_price=Decimal('3.50'))
        oi2 = OrderItem.objects.create(order=order, product=self.p, quantity=1, unit_price=Decimal('7.25'))
        # item subtotal
        self.assertEqual(oi1.subtotal(), Decimal('7.00'))
        self.assertEqual(oi2.subtotal(), Decimal('7.25'))
        # calculate_total on order
        self.assertEqual(order.calculate_total(), Decimal('14.25'))

    def test_order_str_contains_status(self):
        order = Order.objects.create()
        s = str(order)
        self.assertIn('Order(', s)
        self.assertIn('status=', s)
