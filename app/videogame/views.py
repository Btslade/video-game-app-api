"""
Views for the videogame APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Videogame
from videogame import serializers


class VideogameViewSet(viewsets.ModelViewSet):
    """View for manage Videogame APIs"""
    serializer_class = serializers.VideogameDetailSerializer
    queryset = Videogame.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve video games for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.VideogameSerializer  # Expects reference to class not object

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new video game with correct user assigned"""
        serializer.save(user=self.request.user)
