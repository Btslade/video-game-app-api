"""
URL mappings for the videogame app
"""

from django.urls import (
    path,  # Define a path
    include,  # include urls by url names
)

from rest_framework.routers import DefaultRouter

from videogame import views


router = DefaultRouter()
router.register('videogames', views.VideogameViewSet)  # create new endpoint api/videogames
router.register('tags', views.TagViewSet)
router.register('consoles', views.ConsoleViewSet)

app_name = 'videogame'

urlpatterns = [
    path('', include(router.urls)),
]
