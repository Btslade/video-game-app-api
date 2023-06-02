"""
Views for the videogame APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import (
    Videogame,
    Tag,
    Console,
)

from videogame import serializers


class VideogameViewSet(viewsets.ModelViewSet):
    """View for manage Videogame APIs"""
    serializer_class = serializers.VideogameDetailSerializer
    queryset = Videogame.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve video games for authenticated user"""
        tags = self.request.query_params.get('tags')
        consoles = self.request.query_params.get('consoles')
        queryset = self.queryset

        # If below filter provided, convert string ids to int ids
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if consoles:
            console_ids = self._params_to_ints(consoles)
            queryset = queryset.filter(consoles__id__in=console_ids)

        # Filterd result
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.VideogameSerializer  # Expects reference to class not object
        elif self.action == 'upload_image':
            return serializers.VideogameImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new video game with correct user assigned"""
        serializer.save(user=self.request.user)

    # action specifies the different HTTP methods supported by custom action below
    @action(methods=['POST'], detail=True, url_path='upload-image')  # applied to detail view
    def upload_image(self, request, pk=None):
        """Upload an image to Videogame."""
        videogame = self.get_object()
        serializer = self.get_serializer(videogame, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseVideogameAttrViewSet(mixins.DestroyModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """Base viewset for videogame attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseVideogameAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class ConsoleViewSet(BaseVideogameAttrViewSet):
    """Manage consoles in the database."""
    serializer_class = serializers.ConsoleSerializer
    queryset = Console.objects.all()
