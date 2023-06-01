"""
Serializers for the Videogame API view
"""
from rest_framework import serializers

from core.models import (
    Videogame,
    Tag,
    Console,
)


class ConsoleSerializer(serializers.ModelSerializer):
    """Serializer for consoles."""

    class Meta:
        model = Console
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class VideogameSerializer(serializers.ModelSerializer):
    """Serializer for Videogame object"""
    tags = TagSerializer(many=True, required=False)
    consoles = ConsoleSerializer(many=True, required=False)

    class Meta:
        model = Videogame
        fields = ['id', 'title', 'price',
                  'rating', 'players',
                  'genre', 'consoles', 'link', 'tags']

        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, videogame):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            videogame.tags.add(tag_obj)

    def _get_or_create_consoles(self, consoles, videogame):  # internal, user won't call directly
        """Handle getting or creating consoles as needed."""
        auth_user = self.context['request'].user
        for console in consoles:
            console_obj, create = Console.objects.get_or_create(
                user=auth_user,
                **console,
            )
            videogame.consoles.add(console_obj)

    def create(self, validated_data):
        """Create a video game."""
        tags = validated_data.pop('tags', [])
        consoles = validated_data.pop('consoles', [])
        videogame = Videogame.objects.create(**validated_data)
        self._get_or_create_tags(tags, videogame)
        self._get_or_create_consoles(consoles, videogame)

        return videogame

    def update(self, instance, validated_data):
        """Update video game."""
        tags = validated_data.pop('tags', None)
        consoles = validated_data.pop('consoles', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if consoles is not None:
            instance.consoles.clear()
            self._get_or_create_consoles(consoles, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class VideogameDetailSerializer(VideogameSerializer):
    """Serializer for videogame detail view."""

    class Meta(VideogameSerializer.Meta):
        fields = VideogameSerializer.Meta.fields + ['description']
