from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from django.views.generic import TemplateView
from .views import (
    index, MemorialCreateView, MemorialEditView, MyAccountView, update_name,
    update_dates, update_banner, update_quote, memorial_detail, edit_tribute,
    delete_tribute, create_tribute, get_tributes, create_story, edit_story,
    delete_story, get_stories, UpgradeMemorialView, update_biography, plans,
)

app_name = 'memorials'

urlpatterns = [
    # Basic Pages
    path('', index, name='index'),
    path('plans/', plans, name='plans'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('browse/', views.browse_memorials, name='browse'),


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

    # User Account
    path(
        'account/',
        MyAccountView.as_view(),
        name='account_profile',
    ),
    path(
        'memorials/plans/',
        views.plans,
        name='memorial_plans',
    ),
    path(
        'accounts/logout/',
        LogoutView.as_view(next_page='home'),
        name='logout',
    ),
    path(
        'account/edit/',
        views.edit_profile,
        name='edit_profile',
    ),

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
        'memorials/<int:pk>/update-banner/',
        update_banner,
        name='update_banner',
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

    # Audio Handling
    path(
        '<int:pk>/upload-audio/',
        views.upload_audio,
        name='upload_audio',
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

    # Story URLs
    path(
        'memorials/<int:pk>/stories/create/',
        create_story,
        name='create_story',
    ),
    path(
        'memorials/stories/<int:pk>/edit/',
        edit_story,
        name='edit_story',
    ),
    path(
        'memorials/stories/<int:pk>/delete/',
        delete_story,
        name='delete_story',
    ),
    path(
        'memorials/<int:pk>/stories/',
        get_stories,
        name='get_stories',
    ),

    # Upgrade Memorial
    path(
        'memorials/<int:pk>/upgrade/',
        UpgradeMemorialView.as_view(),
        name='upgrade_memorial',
    ),

]
