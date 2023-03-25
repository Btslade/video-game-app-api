"""
URL mappings for the user API
"""
from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [  # Spelling of this variable is critical
    path('create/', views.CreateUserView.as_view(), name='create'),  # Creates user:create
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
