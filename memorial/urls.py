from django.urls import path
from .views import (
    index, MemorialCreateView
)

app_name = 'memorials'

urlpatterns = [
    # Basic Pages
    path('', index, name='index'),

    # Memorial CRUD Operations
    path(
        'memorials/create/',
        MemorialCreateView.as_view(),
        name='memorial_create',
    ),
]