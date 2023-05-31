"""
Tests for the console API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Console

from videogame.serializers import ConsoleSerializer


CONSOLES_URL = reverse('videogame:console-list')


def detail_url(console_id):
    """Create and return a console detail URL."""
    return reverse('videogame:console-detail', args=[console_id])


def create_user(email='user@email.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicConsoleApiTests(TestCase):
    """Test unauthorized API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is requried for retrieving consoles."""
        res = self.client.get(CONSOLES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateConsoleApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_consoles(self):
        Console.objects.create(user=self.user, name='Xbox 360')
        Console.objects.create(user=self.user, name='Gamecube')

        res = self.client.get(CONSOLES_URL)

        consoles = Console.objects.all().order_by('-name')
        serializer = ConsoleSerializer(consoles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_consoles_limited_to_user(self):
        """Test list of consoles is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Console.objects.create(user=user2, name='PS3')
        console = Console.objects.create(user=self.user, name='SNES')

        res = self.client.get(CONSOLES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], console.name)
        self.assertEqual(res.data[0]['id'], console.id)

    def test_update_console(self):
        """Test updating a console."""
        console = Console.objects.create(user=self.user, name='NES')

        payload = {'name': 'SNES'}
        url = detail_url(console.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        console.refresh_from_db()
        self.assertEqual(console.name, payload['name'])
