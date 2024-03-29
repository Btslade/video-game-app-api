"""
Tests for the console API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Console,
    Videogame,
)

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

    def test_delete_console(self):
        """Test deleiting a console."""
        console = Console.objects.create(user=self.user, name='SNES')

        url = detail_url(console.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        consoles = Console.objects.filter(user=self.user)
        self.assertFalse(consoles.exists())

    def test_filter_consoles_assigned_to_videogame(self):
        """Test listing consoles by those assinged to videogames."""
        # Create Consoles
        console1 = Console.objects.create(user=self.user, name='SNES')
        console2 = Console.objects.create(user=self.user, name='NES')  # No videogame assigned

        # Create videogame with only SNES assigned
        videogame = Videogame.objects.create(
            title='Super Mario World',
            price=Decimal('60.00'),
            rating=Decimal('10.00'),
            players=2,
            genre='Platformer',
            user=self.user,
        )
        videogame.consoles.add(console1)

        res = self.client.get(CONSOLES_URL, {'assigned_only': 1})

        # Serialize Consoles
        s1 = ConsoleSerializer(console1)
        s2 = ConsoleSerializer(console2)

        # Validate response data
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_consoles_unique(self):
        """Test filtered consoles returns a unique list."""
        # Create Consoles
        console = Console.objects.create(user=self.user, name='Sega Genesis')
        Console.objects.create(user=self.user, name='Sega Saturn')

        # Create videogames both with Sega Genesis console
        videogame1 = Videogame.objects.create(
            title='Sonic The Hedgehog',
            price=Decimal('60.00'),
            rating=Decimal('10.00'),
            players=2,
            genre='Platformer',
            user=self.user,
        )
        videogame2 = Videogame.objects.create(
            title='Sonic The Hedgehog 2',
            price=Decimal('60.00'),
            rating=Decimal('10.00'),
            players=2,
            genre='Platformer',
            user=self.user,
        )
        videogame1.consoles.add(console)
        videogame2.consoles.add(console)

        # Ensure only one console assigned
        res = self.client.get(CONSOLES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
