from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelUnitTests(TestCase):
    def test_create_user_and_properties(self):
        User = get_user_model()
        u = User.objects.create_user(username='uunit', email='uunit@example.com', password='p', first_name='F', last_name='L')
        self.assertIsNotNone(u.id)
        self.assertEqual(u.email, 'uunit@example.com')
        # username still present even if USERNAME_FIELD=email
        self.assertEqual(u.username, 'uunit')
