"""
Tests for videogame APIs
"""
import os
import tempfile

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Videogame,
    Tag,
    Console,
)

from videogame.serializers import (
    VideogameSerializer,
    VideogameDetailSerializer,
)


VIDEOGAMES_URL = reverse('videogame:videogame-list')


def detail_url(videogame_id):
    """Create and return a videogame URL"""
    return reverse('videogame:videogame-detail', args=[videogame_id])


def image_upload_url(videogame_id):
    """Create and return an image upload URL"""
    return reverse('videogame:videogame-upload-image', args=[videogame_id])


def create_videogame(user, **params):
    """Create and return a smaple video game."""

    defaults = {
        'title'      : 'Sample Video Game',
        'price'      : Decimal('60.00'),
        'rating'     : Decimal('10.00'),
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

    def test_create_tag_on_update(self):
        """Test creating tag when updating a video game."""
        videogame = create_videogame(user=self.user)

        payload = {'tags': [{'name': 'FPS'}]}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='FPS')
        self.assertIn(new_tag, videogame.tags.all())

    def test_update_videogame_assign_tag(self):
        """Test assigning an existing tag when updating a videogmae"""
        tag_fps = Tag.objects.create(user=self.user, name='FPS')
        videogame = create_videogame(user=self.user)
        videogame.tags.add(tag_fps)

        tag_horror = Tag.objects.create(user=self.user, name='Horror')
        payload = {'tags': [{'name': 'Horror'}]}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_horror, videogame.tags.all())
        self.assertNotIn(tag_fps, videogame.tags.all())

    def test_clear_videogame_tags(self):
        """Test clearing a videogame's tags."""
        tag = Tag.objects.create(user=self.user, name='RPG')
        videogame = create_videogame(user=self.user)
        videogame.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(videogame.tags.count(), 0)

    def test_create_videogame_with_new_console(self):
        """Test Creating a videogame with new Console."""
        payload = {
            "title"    : "Call of Duty: Black Ops",
            "price"    : Decimal("60.00"),
            "rating"   : Decimal("10.00"),
            'players'  : 4,
            'genre'    : 'FPS',
            'consoles' : [{'name': 'Xbox 360'}, {'name': 'PS3'}, {'name': 'PC'}, ]
        }
        res = self.client.post(VIDEOGAMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        videogames = Videogame.objects.filter(user=self.user)
        self.assertEqual(videogames.count(), 1)
        videogame = videogames[0]
        self.assertEqual(videogame.consoles.count(), 3)
        for console in payload['consoles']:
            exists = videogame.consoles.filter(
                name=console['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_videogame_with_existing_console(self):
        """Test creating a new videogame with existing console."""
        console = Console.objects.create(user=self.user, name='Xbox One')
        payload = {
            "title"    : "Halo: Infinite",
            "price"    : Decimal("60.00"),
            "rating"   : Decimal("10.00"),
            'players'  : 4,
            'genre'    : 'FPS',
            'consoles' : [{'name': 'Xbox One'}, {'name': 'Xbox Series X'}, {'name': 'PC'}, ]
        }
        res = self.client.post(VIDEOGAMES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        videogames = Videogame.objects.filter(user=self.user)
        self.assertEqual(videogames.count(), 1)
        videogame = videogames[0]
        self.assertEqual(videogame.consoles.count(), 3)
        self.assertIn(console, videogame.consoles.all())
        for console in payload['consoles']:
            exists = videogame.consoles.filter(
                name=console['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_console_on_update(self):
        """Test creating a console when updating a videogame."""
        videogame = create_videogame(user=self.user)

        payload = {'consoles': [{'name': 'Genesis'}]}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_console = Console.objects.get(user=self.user, name='Genesis')
        self.assertIn(new_console, videogame.consoles.all())

    def test_update_videogame_assign_console(self):
        """Test assigning an existing console when updating a videogame"""
        console1 = Console.objects.create(user=self.user, name='Saturn')
        videogame = create_videogame(user=self.user)

        console2 = Console.objects.create(user=self.user, name='Genesis')
        payload = {'consoles': [{'name': 'Genesis'}]}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(console2, videogame.consoles.all())
        self.assertNotIn(console1, videogame.consoles.all())

    def test_clear_videogame_consoles(self):
        """Test clearing a videogame's consoles."""
        console = Console.objects.create(user=self.user, name='SNES')
        videogame = create_videogame(user=self.user)
        videogame.consoles.add(console)

        payload = {'consoles': []}
        url = detail_url(videogame.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(videogame.consoles.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering  videogames by tags"""
        # Video games with tags
        v1 = create_videogame(user=self.user, title='Metroid Prime')
        v2 = create_videogame(user=self.user, title='Halo Infinite')
        tag1 = Tag.objects.create(user=self.user, name='Nintendo')
        tag2 = Tag.objects.create(user=self.user, name='Microsoft')
        v1.tags.add(tag1)
        v2.tags.add(tag2)

        # Video game without a tag
        v3 = create_videogame(user=self.user, title='Call of Duty: Black Ops')

        # Search by tags
        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(VIDEOGAMES_URL, params)

        # Serialize the games
        s1 = VideogameSerializer(v1)
        s2 = VideogameSerializer(v2)
        s3 = VideogameSerializer(v3)

        # Validate results
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_consoles(self):
        """Test filtering videogames by consoles"""
        # Video games with consoles
        v1 = create_videogame(user=self.user, title='Metroid Prime')
        v2 = create_videogame(user=self.user, title='Halo Infinite')
        console1 = Console.objects.create(user=self.user, name='Gamecube')
        console2 = Console.objects.create(user=self.user, name='PC')
        v1.consoles.add(console1)
        v2.consoles.add(console2)

        # Video game without a console
        v3 = create_videogame(user=self.user, title='Call of Duty: Black Ops')

        # Search by consoles
        params = {'consoles': f'{console1.id},{console2.id}'}
        res = self.client.get(VIDEOGAMES_URL, params)

        # Serialize the games
        s1 = VideogameSerializer(v1)
        s2 = VideogameSerializer(v2)
        s3 = VideogameSerializer(v3)

        # Validate results
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.videogame = create_videogame(user=self.user)

    def tearDown(self):
        self.videogame.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a videogame"""
        url = image_upload_url(self.videogame.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))  # create basic 10x10 image
            img.save(image_file, format='JPEG')
            image_file.seek(0)  # seek back to beggining of file to uplaod it
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.videogame.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.videogame.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        url = image_upload_url(self.videogame.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
