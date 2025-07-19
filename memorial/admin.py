from django.contrib import admin
from .models import Memorial, Tribute, GalleryImage, ContactMessage

# --- Admin Registrations ---
admin.site.register(Tribute)  # Basic registration (no custom admin needed)


# --- Inline Admin Classes ---
class GalleryImageInline(admin.TabularInline):
    """Inline editor for memorial gallery images."""
    model = GalleryImage
    extra = 1  # Number of empty image slots shown by default


# --- Custom ModelAdmin Classes ---
@admin.register(Memorial)
class MemorialAdmin(admin.ModelAdmin):
    """Admin interface for Memorials with gallery inline."""
    inlines = [GalleryImageInline]
    # Add other Memorial admin options here as needed


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin interface for contact messages with enhanced list view."""
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)  # Prevent editing of timestamp
    list_editable = ('is_read',)  # Allow bulk read/unread toggle
    date_hierarchy = 'created_at'  # Add date-based navigation
