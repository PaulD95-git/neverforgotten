from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Subscriber


def send_welcome_email(subscriber, request):
    """
    Send a welcome email to new subscribers.
    
    Args:
        subscriber: Subscriber object to welcome
        request: HttpRequest object for building absolute URLs
        
    Returns:
        None
    """
    unsubscribe_url = request.build_absolute_uri(
        reverse('newsletter:unsubscribe', args=[subscriber.email])
    )
    
    context = {
        'subscriber': subscriber,
        'unsubscribe_url': unsubscribe_url,
        'welcome_message': "Thank you for joining our community!",
        'features': [
            "New memorial features",
            "Community stories",
            "Special announcements"
        ]
    }
    
    subject = "Welcome to NeverForgotten!"
    html_content = render_to_string(
        'newsletter/emails/welcome_email.html',
        context
    )
    text_content = strip_tags(html_content)
    
    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        html_message=html_content,
        fail_silently=False
    )


def send_newsletter(newsletter, request):
    """
    Send a newsletter to all active subscribers.
    
    Args:
        newsletter: Newsletter object to send
        request: HttpRequest object for building absolute URLs
        
    Returns:
        int: Number of successfully sent emails
    """
    subscribers = Subscriber.objects.filter(subscribed=True)
    sent_count = 0
    
    for subscriber in subscribers:
        try:
            unsubscribe_url = request.build_absolute_uri(
                reverse('newsletter:unsubscribe', args=[subscriber.email])
            )
            
            context = {
                'newsletter': newsletter,
                'subscriber': subscriber,
                'unsubscribe_url': unsubscribe_url,
            }
            
            # Render both text and HTML versions
            text_content = render_to_string(
                'newsletter/emails/newsletter_template.txt',
                context
            )
            html_content = render_to_string(
                'newsletter/emails/newsletter_template.html',
                context
            )
            
            # Create and send email
            msg = EmailMultiAlternatives(
                subject=newsletter.subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            sent_count += 1
            
        except Exception as e:
            # Consider using Django's logging instead of print
            print(f"Failed to send to {subscriber.email}: {str(e)}")
            continue
    
    # Update newsletter status
    newsletter.is_sent = True
    newsletter.sent_at = timezone.now()
    newsletter.save()
    
    return sent_count


def send_confirmation_email(subscriber, request):
    """
    Send subscription confirmation email to new subscribers.
    
    Args:
        subscriber: Subscriber object to confirm
        request: HttpRequest object for building absolute URLs
        
    Returns:
        None
    """
    unsubscribe_url = request.build_absolute_uri(
        reverse('newsletter:unsubscribe', args=[subscriber.email])
    )
    
    context = {
        'subscriber': subscriber,
        'unsubscribe_url': unsubscribe_url,
    }
    
    subject = "Thanks for subscribing to our newsletter"
    text_content = render_to_string(
        'newsletter/emails/subscription_confirmation.txt',
        context
    )
    html_content = render_to_string(
        'newsletter/emails/subscription_confirmation.html',
        context
    )
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()