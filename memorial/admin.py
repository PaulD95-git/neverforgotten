from django.contrib import admin

# Register your models here.
from .models import Memorial
@admin.register(Memorial)
class MemorialAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death', 'user')
    search_fields = ('first_name', 'last_name')
    list_filter = ('date_of_birth', 'date_of_death')
    ordering = ('-date_of_death',)
    date_hierarchy = 'date_of_death'