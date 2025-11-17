from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from .models import Category, Product, Favorite, Rating

User = get_user_model()


class ProductCatalogTests(APITestCase):
	def setUp(self):
		self.category = Category.objects.create(title='Shoes')
		self.other_category = Category.objects.create(title='Accessories')

		self.product_a = Product.objects.create(
			title='Runner',
			description='Running shoes',
			brand='Speedster',
			price=Decimal('99.99'),
			category=self.category,
			rating=Decimal('4.00'),
			stock_quantity=10,
			in_stock=True,
		)
		self.product_b = Product.objects.create(
			title='Walker',
			description='Walking shoes',
			brand='ComfortCo',
			price=Decimal('79.99'),
			category=self.category,
			rating=Decimal('5.00'),
			stock_quantity=5,
			in_stock=True,
		)
		self.product_c = Product.objects.create(
			title='Socks',
			description='Warm socks',
			brand='WarmFeet',
			price=Decimal('9.99'),
			category=self.other_category,
			rating=Decimal('3.00'),
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

	def test_filter_by_brand(self):
		response = self.client.get(self.list_url, {'brand': self.product_a.brand})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		results = response.data['results']
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]['id'], str(self.product_a.id))


class FavoriteTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='fav@example.com',
			username='favourite',
			password='StrongPass123!',
			first_name='Fav',
			last_name='User',
		)
		self.category = Category.objects.create(title='Bags')
		self.product = Product.objects.create(
			title='Backpack',
			description='Travel backpack',
			brand='CarryAll',
			price=Decimal('49.99'),
			category=self.category,
			rating=Decimal('0.00'),
			stock_quantity=20,
			in_stock=True,
		)
		self.list_url = reverse('favorite-list')
		self.delete_url = reverse('favorite-delete', kwargs={'product_id': self.product.pk})

	def test_add_and_list_favorites(self):
		self.client.force_authenticate(user=self.user)

		create_response = self.client.post(self.list_url, {'product_id': self.product.pk}, format='json')
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Favorite.objects.filter(user=self.user, product=self.product).exists())

		list_response = self.client.get(self.list_url)
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual(list_response.data['count'], 1)
		self.assertEqual(list_response.data['results'][0]['product']['id'], str(self.product.pk))

	def test_remove_favorite(self):
		Favorite.objects.create(user=self.user, product=self.product)
		self.client.force_authenticate(user=self.user)

		delete_response = self.client.delete(self.delete_url)
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Favorite.objects.filter(user=self.user, product=self.product).exists())


class RatingTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='rate@example.com',
			username='rateuser',
			password='StrongPass123!',
			first_name='Rate',
			last_name='User',
		)
		self.category = Category.objects.create(title='Electronics')
		self.product = Product.objects.create(
			title='Headphones',
			description='Noise cancelling',
			brand='SoundMax',
			price=Decimal('199.99'),
			category=self.category,
			rating=Decimal('0.00'),
			stock_quantity=15,
			in_stock=True,
		)
		self.rate_url = reverse('product-rate', kwargs={'pk': self.product.pk})
		self.list_url = reverse('product-rating-list', kwargs={'pk': self.product.pk})

	def test_create_and_update_rating(self):
		self.client.force_authenticate(user=self.user)

		create_response = self.client.post(self.rate_url, {'score': 5, 'review': 'Great sound'}, format='json')
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		self.product.refresh_from_db()
		self.assertEqual(self.product.rating_count, 1)
		self.assertEqual(str(self.product.rating), '5.00')

		update_response = self.client.post(self.rate_url, {'score': 3}, format='json')
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.product.refresh_from_db()
		self.assertEqual(self.product.rating_count, 1)
		self.assertEqual(str(self.product.rating), '3.00')

	def test_delete_rating_resets_stats(self):
		Rating.objects.create(user=self.user, product=self.product, score=4)
		self.product.update_rating_stats()
		self.client.force_authenticate(user=self.user)

		delete_response = self.client.delete(self.rate_url)
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.product.refresh_from_db()
		self.assertEqual(self.product.rating_count, 0)
		self.assertEqual(str(self.product.rating), '0.00')

	def test_list_ratings(self):
		other_user = User.objects.create_user(
			email='another@example.com',
			username='anotheruser',
			password='StrongPass123!',
			first_name='Another',
			last_name='User',
		)
		Rating.objects.create(user=self.user, product=self.product, score=4, review='Nice')
		Rating.objects.create(user=other_user, product=self.product, score=5, review='Excellent')
		self.product.update_rating_stats()

		response = self.client.get(self.list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['results']), 2)
