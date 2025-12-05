from decimal import Decimal

from django.test import TestCase

from apps.catalog.models import Product, Category, Rating


class CatalogModelUnitTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(title='unit-cat')
        self.p = Product.objects.create(
            title='P',
            description='desc',
            brand='B',
            price=Decimal('7.00'),
            category=self.cat,
            rating=Decimal('0.00'),
            stock_quantity=3,
            in_stock=True,
        )

    def test_reserve_and_release_quantity(self):
        # reserve available quantity
        ok = self.p.reserve_quantity(2)
        self.assertTrue(ok)
        self.p.refresh_from_db()
        self.assertEqual(self.p.stock_quantity, 1)
        self.assertTrue(self.p.in_stock)

        # reserve remaining
        ok = self.p.reserve_quantity(1)
        self.assertTrue(ok)
        self.p.refresh_from_db()
        self.assertEqual(self.p.stock_quantity, 0)
        self.assertFalse(self.p.in_stock)

        # cannot reserve more than available
        ok = self.p.reserve_quantity(1)
        self.assertFalse(ok)

        # release back and check in_stock toggles
        self.p.release_quantity(5)
        self.p.refresh_from_db()
        self.assertGreater(self.p.stock_quantity, 0)
        self.assertTrue(self.p.in_stock)

    def test_update_rating_stats(self):
        # create two ratings and update stats
        user1 = None
        user2 = None
        # Rating expects a user; create anonymous users via minimal User stub if needed
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user1 = User.objects.create_user(username='r1', email='r1@example.com', password='p', first_name='A', last_name='B')
        user2 = User.objects.create_user(username='r2', email='r2@example.com', password='p', first_name='C', last_name='D')
        Rating.objects.create(user=user1, product=self.p, score=4)
        Rating.objects.create(user=user2, product=self.p, score=5)
        self.p.update_rating_stats()
        self.p.refresh_from_db()
        self.assertEqual(self.p.rating_count, 2)
        # average of 4 and 5 is 4.5 -> quantized to two decimals
        self.assertEqual(self.p.rating, Decimal('4.50'))
