"""
Tests for models
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """ Test Models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))  # Check password via hashing system

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'smaple123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """User must have an email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='test123'
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_videogame(self):
        """Test creating a video game is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        video_game = models.Videogame.objects.create(
            user=user,
            title='Sample video game name',
            price=Decimal('60.00'),
            rating=Decimal('4.5'),
            players=4,
            genre='FPS',
            description='Sample video game description',
            link='Sample link'
        )

        self.assertEqual(str(video_game), video_game.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_console(self):
        """Test creating a console is successful"""
        user = create_user()
        console = models.Console.objects.create(
            user=user,
            name="Gamecube",
            price=Decimal('100.00'),
            rating=Decimal('10.0'),
        )

        self.assertEqual(str(console), console.name)

    @patch('core.models.uuid.uuid4')  # mock the behaviour of creating a unique identifier (UID)
    def test_videogame_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'  # mocked response
        mock_uuid.return_value = uuid
        file_path = models.videogame_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/videogame/{uuid}.jpg')
