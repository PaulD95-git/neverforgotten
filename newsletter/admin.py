from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages

from .models import Subscriber, Newsletter
from .utils import send_newsletter


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """Admin interface configuration for Subscriber model."""
    
    list_display = ('email', 'first_name', 'subscribed', 'created_at')
    list_filter = ('subscribed', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    actions = ['resubscribe_selected']

    def resubscribe_selected(self, request, queryset):
        """
        Admin action to resubscribe selected subscribers.
        
        Args:
            request: HttpRequest object
            queryset: QuerySet of selected Subscriber objects
        """
        updated = queryset.update(subscribed=True)
        self.message_user(
            request,
            f'{updated} subscribers were resubscribed.',
            messages.SUCCESS
        )
    
    resubscribe_selected.short_description = "Resubscribe selected subscribers"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin interface configuration for Newsletter model."""
    
    list_display = (
        'subject',
        'created_at',
        'is_sent',
        'sent_at',
        'send_newsletter_link'
    )
    list_filter = ('is_sent', 'created_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('is_sent', 'sent_at')
    actions = ['send_selected_newsletters']

    def send_newsletter_link(self, obj):
        """
        Custom admin column that displays a 'Send Now' button for unsent newsletters.
        
        Args:
            obj: Newsletter instance
            
        Returns:
            HTML button or status text
        """
        if not obj.is_sent:
            return format_html(
                '<a class="button" href="{}">Send Now</a>',
                reverse('admin:send_newsletter', args=[obj.pk])
            )
        return "Sent"
    
    send_newsletter_link.short_description = "Actions"
    send_newsletter_link.allow_tags = True

    def get_urls(self):
        """Adds custom URLs to the admin interface."""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send/',
                self.admin_site.admin_view(self.send_newsletter),
                name='send_newsletter'
            ),
        ]
        return custom_urls + urls

    def send_newsletter(self, request, object_id):
        """
        Custom admin view to send a single newsletter.
        
        Args:
            request: HttpRequest object
            object_id: ID of the Newsletter to send
            
        Returns:
            Redirect response
        """
        newsletter = Newsletter.objects.get(pk=object_id)
        try:
            send_newsletter(newsletter, request)
            newsletter.is_sent = True
            newsletter.save()
            self.message_user(
                request,
                f'Newsletter "{newsletter.subject}" sent successfully!',
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f'Error: {str(e)}',
                level=messages.ERROR
            )
        return redirect('..')

    def send_selected_newsletters(self, request, queryset):
        """
        Admin action to send multiple selected newsletters.
        
        Args:
            request: HttpRequest object
            queryset: QuerySet of selected Newsletter objects
        """
        sent_count = 0
        for newsletter in queryset.filter(is_sent=False):
            try:
                send_newsletter(newsletter, request)
                newsletter.is_sent = True
                newsletter.save()
                sent_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Failed to send {newsletter.subject}: {e}',
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f'Sent {sent_count} out of {queryset.count()} newsletters',
            messages.SUCCESS
        )
    
    send_selected_newsletters.short_description = "Send selected newsletters"