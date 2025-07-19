# memorial/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    index,
    MemorialCreateView,
    MemorialEditView,
    memorial_detail,
    delete_memorial,
    MyAccountView,
    edit_profile,
    UpgradeMemorialView,
)

app_name = 'memorials'

urlpatterns = [
    # Home page
    path('', index, name='index'),

    # Memorial CRUD Operations
    path('memorials/create/', MemorialCreateView.as_view(), name='memorial_create'),
    path('memorials/<int:pk>/edit/', MemorialEditView.as_view(), name='memorial_edit'),
    path('<int:pk>/delete/', delete_memorial, name='memorial_delete'),
    path('memorials/<int:pk>/', memorial_detail, name='memorial_detail'),

    # User Account
    path('account/', MyAccountView.as_view(), name='account_profile'),
    path('account/edit/', edit_profile, name='edit_profile'),
    path('accounts/logout/', LogoutView.as_view(next_page='memorials:index'), name='logout'),

    # Upgrade Memorial
    path('<int:pk>/upgrade/', UpgradeMemorialView.as_view(), name='upgrade'),

    # Memorial Media Updates
    path(
        '<int:pk>/upload-profile-picture/',
        views.upload_profile_picture,
        name='upload_profile_picture',
    ),

]