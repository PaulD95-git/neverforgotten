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
    update_name,
    update_dates,
    update_biography,
    update_quote,
    delete_memorial,
    create_tribute,
    delete_tribute,
    edit_tribute,
    get_tributes,
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
    path(
        'memorials/<int:pk>/update-name/',
        update_name,
        name='update_name',
    ),
    path(
        'memorials/<int:pk>/update-dates/',
        update_dates,
        name='update_dates',
    ),
    path(
        'memorials/<int:pk>/update-quote/',
        update_quote,
        name='update_quote',
    ),
    path(
        'memorials/<int:pk>/update-biography/',
        update_biography,
        name='update_biography',
    ),
    # Tribute URLs
    path(
        'memorials/<int:pk>/tributes/create/',
        create_tribute,
        name='create_tribute',
    ),
    path(
        'memorials/tributes/<int:pk>/edit/',
        edit_tribute,
        name='edit_tribute',
    ),
    path(
        'memorials/tributes/<int:pk>/delete/',
        delete_tribute,
        name='delete_tribute',
    ),
    path(
        'memorials/<int:pk>/tributes/',
        get_tributes,
        name='get_tributes',
    ),
    # Gallery Management
    path(
        'memorials/<int:pk>/upload-gallery/',
        views.upload_gallery_images,
        name='upload_gallery_images',
    ),
    path(
        '<int:memorial_id>/gallery/<int:image_id>/delete/',
        views.delete_gallery_image,
        name='delete_gallery_image',
    ),

]