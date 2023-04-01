"""
Serializers for the Videogame API view
"""
from rest_framework import serializers

from core.models import Videogame


class VideogameSerializer(serializers.ModelSerializer):
    """ Serializer for Videogame object"""

    class Meta:
        model = Videogame
        fields = ['id', 'title', 'price',
                  'rating', 'system', 'players',
                  'genre', 'description', 'link']

        read_only_fields = ['id']
