from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.catalog.models import Product, Category
from .models import Comment


class CommentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user1 = User.objects.create_user(username='u1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='u2', email='u2@example.com', password='pass')

        self.category = Category.objects.create(title='c1', description='cat')
        self.product = Product.objects.create(title='p1', description='prod', price=1.00, category=self.category)

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(self.user1)
        url = reverse('product-comments', kwargs={'product_id': self.product.id})
        resp = self.client.post(url, {'text': 'hello'})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.first()
        self.assertEqual(c.text, 'hello')
        self.assertEqual(c.user, self.user1)

    def test_update_comment_owner(self):
        c = Comment.objects.create(product=self.product, user=self.user1, text='orig')
        url = reverse('comment-detail', kwargs={'id': c.id})
        self.client.force_authenticate(self.user1)
        resp = self.client.patch(url, {'text': 'new'})
        self.assertEqual(resp.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.text, 'new')

    def test_update_comment_forbidden_other_user(self):
        c = Comment.objects.create(product=self.product, user=self.user1, text='orig')
        url = reverse('comment-detail', kwargs={'id': c.id})
        self.client.force_authenticate(self.user2)
        resp = self.client.patch(url, {'text': 'hacked'})
        self.assertIn(resp.status_code, (403, 401))

    def test_delete_comment_owner(self):
        c = Comment.objects.create(product=self.product, user=self.user1, text='orig')
        url = reverse('comment-detail', kwargs={'id': c.id})
        self.client.force_authenticate(self.user1)
        resp = self.client.delete(url)
        self.assertIn(resp.status_code, (204, 200))
        self.assertEqual(Comment.objects.count(), 0)
