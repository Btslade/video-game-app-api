"""
Tests for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


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
            system='Gamecube',
            players=4,
            genre='FPS',
            description='Sample video game description',
            link='Sample link'
        )

        self.assertEqual(str(video_game), video_game.title)
