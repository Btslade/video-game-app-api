"""
Views for the recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Videogame
from videogame import serializers


class VideogameViewSet(viewsets.ModelViewSet):
    """View for manage Videogame APIs"""
    serializer_class = serializers.VideogameSerializer
    queryset = Videogame.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve video games for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
