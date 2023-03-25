"""
Views for the user API.
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):  # handle POST for creating objects in database
    """ Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):  # Default uses username and password
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer  # Overrides to use email and password
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # Use default class for token view
