from django.urls import path
from . import views
from .views import MemorialCreateView, MemorialEditView, memorial_detail

app_name = 'memorials'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),

        # Memorial CRUD Operations
    path(
        'memorials/create/',
        MemorialCreateView.as_view(),
        name='memorial_create',
    ),
    path(
        'memorials/<int:pk>/edit/',
        MemorialEditView.as_view(),
        name='memorial_edit',
    ),
    path(
        '<int:pk>/delete/',
        views.delete_memorial,
        name='memorial_delete',
    ),
    path(
        'memorials/<int:pk>/',
        memorial_detail,
        name='memorial_detail',
    ),

    # Upgrade Memorial
    path('<int:pk>/upgrade/', views.UpgradeMemorialView.as_view(), name='upgrade'),
]
