"""
Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email address')

        # self.model is the same is creating a new user
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  # supports adding multiple databases

        return user

    def create_superuser(self, email, password):
        """create and return a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()   # Assigns UserManager to this class

    USERNAME_FIELD = 'email'  # Must be defined or else attribute error occurs


class Videogame(models.Model):
    """Videogame object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Defined in settings.py
        on_delete=models.CASCADE,  # If user deleted, models associated with user deleted too
    )
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    console = models.ManyToManyField('Console')
    players = models.IntegerField()
    genre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering video games."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Console(models.Model):
    """Console object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Defined in settings.py
        on_delete=models.CASCADE,  # If user deleted, models associated with user deleted too
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name
