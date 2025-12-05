from django.test import TestCase

from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Product
from apps.comments.models import Comment


class CommentsModelUnitTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(title='c1')
        self.p = Product.objects.create(title='prod', description='d', brand='b', price=1.00, category=self.cat)
        User = get_user_model()
        self.u = User.objects.create_user(username='cu', email='cu@example.com', password='p', first_name='A', last_name='B')

    def test_create_and_str(self):
        c = Comment.objects.create(product=self.p, user=self.u, text='hello')
        s = str(c)
        self.assertIn('Comment by', s)
        self.assertIn(str(self.u), s)
