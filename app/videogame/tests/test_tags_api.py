"""
Tests for the tags API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Videogame,
)

from videogame.serializers import TagSerializer

TAGS_URL = reverse('videogame:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('videogame:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsapiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='FPS')
        Tag.objects.create(user=self.user, name='Adventure')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')  # reverse name order
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Horror')
        tag = Tag.objects.create(user=self.user, name='RPG')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='Horror')

        payload = {'name': 'FPS'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='JRPG')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_videogame(self):
        """Test listing tags by those assinged to videogames."""
        # Create Tags
        tag1 = Tag.objects.create(user=self.user, name='Nintendo')
        tag2 = Tag.objects.create(user=self.user, name='Sega')  # No videogame assigned

        # Create videogame with only Nintendo assigned
        videogame = Videogame.objects.create(
            title='Super Mario World',
            price=Decimal('60.00'),
            rating=Decimal('10.00'),
            players=2,
            genre='Platformer',
            user=self.user,
        )
        videogame.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Serialize Tags
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        # Validate response data
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_tags_unique(self):
        """Test filtered consoles returns a unique list."""
        # Create Tags
        tag = Tag.objects.create(user=self.user, name='Sega')
        Tag.objects.create(user=self.user, name='Nintendo')

        # Create videogames both with Sega tag
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
        videogame1.tags.add(tag)
        videogame2.tags.add(tag)

        # Ensure only one tag assigned
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
