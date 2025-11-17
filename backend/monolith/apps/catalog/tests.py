from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductCatalogTests(APITestCase):
	def setUp(self):
		self.category = Category.objects.create(title='Shoes')
		self.other_category = Category.objects.create(title='Accessories')

		self.product_a = Product.objects.create(
			title='Runner',
			description='Running shoes',
			price=Decimal('99.99'),
			category=self.category,
			rating=4,
			stock_quantity=10,
			in_stock=True,
		)
		self.product_b = Product.objects.create(
			title='Walker',
			description='Walking shoes',
			price=Decimal('79.99'),
			category=self.category,
			rating=5,
			stock_quantity=5,
			in_stock=True,
		)
		self.product_c = Product.objects.create(
			title='Socks',
			description='Warm socks',
			price=Decimal('9.99'),
			category=self.other_category,
			rating=3,
			stock_quantity=50,
			in_stock=True,
		)

		self.list_url = reverse('product-list')
		self.detail_url = reverse('product-detail', kwargs={'pk': self.product_a.pk})

	def test_product_list_sort_by_price_desc(self):
		response = self.client.get(self.list_url, {'sort': 'price_desc'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ids = [item['id'] for item in response.data['results']]
		self.assertEqual(ids[0], str(self.product_a.id))
		self.assertEqual(ids[1], str(self.product_b.id))

	def test_product_list_sort_by_rating(self):
		response = self.client.get(self.list_url, {'sort': 'rating_desc'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ids = [item['id'] for item in response.data['results']]
		self.assertEqual(ids[0], str(self.product_b.id))
		self.assertEqual(ids[1], str(self.product_a.id))

	def test_product_detail_includes_recommendations(self):
		response = self.client.get(self.detail_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		recommendations = response.data['recommendations']
		recommended_ids = {item['id'] for item in recommendations}
		self.assertIn(str(self.product_b.id), recommended_ids)
		self.assertNotIn(str(self.product_a.id), recommended_ids)
		self.assertNotIn(str(self.product_c.id), recommended_ids)

	def test_unknown_sort_falls_back_to_default(self):
		response_default = self.client.get(self.list_url)
		response_unknown = self.client.get(self.list_url, {'sort': 'unknown'})

		self.assertEqual(response_default.status_code, status.HTTP_200_OK)
		self.assertEqual(response_unknown.status_code, status.HTTP_200_OK)
		self.assertEqual(
			[item['id'] for item in response_default.data['results']],
			[item['id'] for item in response_unknown.data['results']],
		)
