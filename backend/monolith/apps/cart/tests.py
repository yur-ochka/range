from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Category, Product


class CartTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test')
        self.product = Product.objects.create(
            title='Test Product',
            description='Just for tests',
            brand='TestBrand',
            price=Decimal('10.00'),
            category=self.category,
            rating=Decimal('0.00'),
            stock_quantity=5,
            in_stock=True,
        )
        self.cart_url = reverse('cart-detail')
        self.items_url = reverse('cart-items-add')

    def test_get_cart_anonymous(self):
        resp = self.client.get(self.cart_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # cart should contain id and items list
        self.assertIn('id', resp.data)
        self.assertIn('items', resp.data)

    def test_add_item_creates_cart_item(self):
        resp = self.client.post(self.items_url, {'product_id': str(self.product.id), 'quantity': 2}, format='json')
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        data = resp.data
        self.assertEqual(data['product_id'], str(self.product.id))
        self.assertEqual(data['quantity'], 2)
