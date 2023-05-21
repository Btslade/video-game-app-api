"""
Tests for videogame APIs
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Videogame,
    Tag
)

from videogame.serializers import (
    VideogameSerializer,
    VideogameDetailSerializer,
)


VIDEOGAMES_URL = reverse('videogame:videogame-list')


def detail_url(videogame_id):
    """Create and return a videogame URL"""
    return reverse('videogame:videogame-detail', args=[videogame_id])


def create_videogame(user, **params):
    """Create and return a smaple video game."""

    defaults = {
        'title'      : 'Sample Video Game',
        'price'      : Decimal('60.00'),
        'rating'     : Decimal('10.00'),
        'system'     : 'Sample System',
        'players'    : 4,
        'genre'      : 'FPS',
        'description': 'Sample description',
        'link'       : 'http://example.com/videogame.pdf',
    }
    defaults.update(params)

    videogame = Videogame.objects.create(user=user, **defaults)
    return videogame


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_videogames(self):
        """Test retrieving a list of video games."""
        create_videogame(user=self.user)
        create_videogame(user=self.user)

        res = self.client.get(VIDEOGAMES_URL)

        videogames = Videogame.objects.all().order_by('-id')  # reverse id order
        serializer = VideogameSerializer(videogames, many=True)  # many allows for multiple items
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Data dict of objects passed via serializer

    def test_videogame_list_limited_to_user(self):
        """Test list of video games is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        create_videogame(user=other_user)
        create_videogame(user=self.user)

        res = self.client.get(VIDEOGAMES_URL)

        videogames = Videogame.objects.filter(user=self.user)
        serializer = VideogameSerializer(videogames, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_videogame_detail(self):
        """Test get video game detail"""
        videogame = create_videogame(user=self.user)

        url = detail_url(videogame.id)
        res = self.client.get(url)

        serializer = VideogameDetailSerializer(videogame)
        self.assertEqual(res.data, serializer.data)

    def test_create_videogame(self):
        """Test creating a video game"""
        payload = {
            "title"  : "Sample Video Game",
            "price"  : Decimal("60.00"),
            "rating" : Decimal("10.00"),
            'system' : 'Sample System',
            'players': 4,
            'genre'  : 'FPS',
        }

        res = self.client.post(VIDEOGAMES_URL, payload)  # /api/videogame/videogame

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        videogame = Videogame.objects.get(id=res.data['id'])
        for k, v in payload.items():  # k=key v=value
            self.assertEqual(getattr(videogame, k), v)  # get attribute without dot notation
        self.assertEqual(videogame.user, self.user)

    def test_partial_update(self):
        """Test partial update of a video game"""
        original_link = "https://example.com/vidogame.pdf"
        videogame = create_videogame(
            user=self.user,
            title='Sample video game title',
            link=original_link,
        )

        payload = {'title': "New Video Game Title"}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        videogame.refresh_from_db()
        self.assertEqual(videogame.title, payload['title'])
        self.assertEqual(videogame.link, original_link)
        self.assertEqual(videogame.user, self.user)

    def test_full_update(self):
        """Test full update of a video game"""
        videogame = create_videogame(
            user=self.user,
            title='Sample video game title',
            link='https://example.com/videogame.pdf',
        )

        payload = {
            'title'       : 'New Video Game Title',
            'price'       : Decimal("70.00"),
            'rating'      : Decimal("2.23"),
            'system'      : 'Sample System',
            'players'     : 2,
            'genre'       : 'Horror',
            'description' : 'Updated description',
            'link'        : 'https://example.com/new-videogame.pdf',
        }

        url = detail_url(videogame.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        videogame.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(videogame, k), v)
        self.assertEqual(videogame.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the video game user results in an error"""
        new_user = create_user(email='user2@example.com', password='test123')
        videogame = create_videogame(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(videogame.id)
        self.client.patch(url, payload)

        videogame.refresh_from_db()
        self.assertEqual(videogame.user, self.user)

    def test_delete_videogame(self):
        """Test deleting a video game successful"""
        videogame = create_videogame(user=self.user)

        url = detail_url(videogame.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Videogame.objects.filter(id=videogame.id).exists())

    def test_delete_other_users_videogame_error(self):
        """Test trying to delete another users videogame gives error"""
        new_user = create_user(email='user2@example.com', password='test123')
        videogame = create_videogame(user=new_user)

        url = detail_url(videogame.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Videogame.objects.filter(id=videogame.id).exists())

    def test_create_videogame_with_new_tag(self):
        """Test creating a videogame with new tags."""
        payload = {
            "title"  : "Halo 3",
            "price"  : Decimal("60.00"),
            "rating" : Decimal("10.00"),
            'system' : 'Xbox 360',
            'players': 4,
            'genre'  : 'FPS',
            'tags'   : [{'name': 'FPS'}, {'name': 'Xbox 360'}]
        }
        res = self.client.post(VIDEOGAMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        videogames = Videogame.objects.filter(user=self.user)
        self.assertEqual(videogames.count(), 1)
        videogame = videogames[0]
        self.assertEqual(videogame.tags.count(), 2)
        for tag in payload['tags']:
            exists = videogame.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_videogame_with_existing_tags(self):
        """Test creating a video game with existing tag."""
        tag_fps = Tag.objects.create(user=self.user, name='FPS')
        payload = {
            "title"  : "Halo 3",
            "price"  : Decimal("60.00"),
            "rating" : Decimal("10.00"),
            'system' : 'Xbox 360',
            'players': 4,
            'genre'  : 'FPS',
            'tags'   : [{'name': 'FPS'}, {'name': 'Xbox 360'}]
        }
        res = self.client.post(VIDEOGAMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        videogames = Videogame.objects.filter(user=self.user)
        self.assertEqual(videogames.count(), 1)
        videogame = videogames[0]
        self.assertEqual(videogame.tags.count(), 2)
        self.assertIn(tag_fps, videogame.tags.all())
        for tag in payload['tags']:
            exists = videogame.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
