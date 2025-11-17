from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='StrongPass123!',
            first_name='Test',
            last_name='User',
        )
        self.reset_url = reverse('password-reset')
        self.confirm_url = reverse('password-reset-confirm')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_email(self):
        response = self.client.post(self.reset_url, {'email': self.user.email}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('reset-password', mail.outbox[0].body)

    def test_password_reset_confirm_updates_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.post(
            self.confirm_url,
            {
                'uid': uid,
                'token': token,
                'new_password': 'NewStrongPass123!',
                're_new_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass123!'))

    def test_password_reset_confirm_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(
            self.confirm_url,
            {
                'uid': uid,
                'token': 'invalid-token',
                'new_password': 'NewStrongPass123!',
                're_new_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='auth@example.com',
            username='authuser',
            password='StrongPass123!',
            first_name='Auth',
            last_name='User',
        )
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.profile_update_url = reverse('profile-update')
        self.refresh_url = reverse('refresh')

    def test_register_creates_user_and_profile(self):
        payload = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'AnotherStrongPass123!',
            'password_confirm': 'AnotherStrongPass123!',
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=payload['email']).exists())
        created_user = User.objects.get(email=payload['email'])
        self.assertTrue(hasattr(created_user, 'profile'))

    def test_login_returns_tokens(self):
        response = self.client.post(
            self.login_url,
            {'email': self.user.email, 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'email': self.user.email, 'password': 'WrongPassword'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_retrieve_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_update_url,
            {'phone': '+380123456789'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '+380123456789')

    def test_refresh_token_returns_new_access(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            self.refresh_url,
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
