"""
Serializers for the Videogame API view
"""
from rest_framework import serializers

from core.models import (
    Videogame,
    Tag)


class VideogameSerializer(serializers.ModelSerializer):
    """ Serializer for Videogame object"""

    class Meta:
        model = Videogame
        fields = ['id', 'title', 'price',
                  'rating', 'system', 'players',
                  'genre', 'link']

        read_only_fields = ['id']


class VideogameDetailSerializer(VideogameSerializer):
    """Serializer for videogame detail view."""

    class Meta(VideogameSerializer.Meta):
        fields = VideogameSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
