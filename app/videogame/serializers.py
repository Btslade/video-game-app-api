"""
Serializers for the Videogame API view
"""
from rest_framework import serializers

from core.models import (
    Videogame,
    Tag
)


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class VideogameSerializer(serializers.ModelSerializer):
    """ Serializer for Videogame object"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Videogame
        fields = ['id', 'title', 'price',
                  'rating', 'system', 'players',
                  'genre', 'link', 'tags']

        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a video game."""
        tags = validated_data.pop('tags', [])
        videogame = Videogame.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )

            videogame.tags.add(tag_obj)

        return videogame


class VideogameDetailSerializer(VideogameSerializer):
    """Serializer for videogame detail view."""

    class Meta(VideogameSerializer.Meta):
        fields = VideogameSerializer.Meta.fields + ['description']
