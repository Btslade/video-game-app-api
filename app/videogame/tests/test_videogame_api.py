"""
Tests for videogame APIs
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Videogame

from videogame.serializers import VideogameSerializer


VIDEOGAMES_URL = reverse('videogame:videogame-list')


def create_videogame(user, **params):
    """Create and return a smaple video game."""

    defaults = {
        'title': 'Sample Video Game',
        'price': Decimal('60.00'),
        'rating': Decimal('10.00'),
        'system': 'Sample System',
        'players': 4,
        'genre': 'FPS',
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    videogame = Videogame.objects.create(user=user, **defaults)
    return videogame


class PublicVideogameAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(VIDEOGAMES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVideogameAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_videogames(self):
        """Test retrieving a list of videogames."""
        create_videogame(user=self.user)
        create_videogame(user=self.user)

        res = self.client.get(VIDEOGAMES_URL)

        videogames = Videogame.objects.all().order_by('-id')  # reverse id order
        serializer = VideogameSerializer(videogames, many=True)  # many allows for multiple items
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Data dict of objects passed via serializer

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_videogame(user=other_user)
        create_videogame(user=self.user)

        res = self.client.get(VIDEOGAMES_URL)

        videogames = Videogame.objects.filter(user=self.user)
        serializer = VideogameSerializer(videogames, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
