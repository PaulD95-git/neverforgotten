from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import Subscriber
from .forms import SubscribeForm
from .utils import send_welcome_email


def subscribe(request):
    """
    Handle newsletter subscription requests.
    
    Processes both new subscriptions and resubscriptions,
    with appropriate email confirmation.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('memorials:index')

    form = SubscribeForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid form submission')
        return redirect('memorials:index')

    try:
        email = form.cleaned_data['email']
        first_name = form.cleaned_data.get('first_name', '')
        last_name = form.cleaned_data.get('last_name', '')

        # Get or create subscriber
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'subscribed': True
            }
        )

        if not created:
            if not subscriber.subscribed:
                # Resubscribe existing inactive subscriber
                subscriber.subscribed = True
                subscriber.save()
                messages.info(request, 'You have been resubscribed to our newsletter.')
            else:
                messages.info(request, 'You are already subscribed.')
                return redirect('memorials:index')

        # Send welcome email for new or resubscribed users
        send_welcome_email(subscriber, request)
        messages.success(
            request,
            'Thank you for subscribing! Please check your email.'
        )
        return redirect('memorials:index')

    except Exception as e:
        messages.error(
            request,
            'Subscription failed. Please try again later.'
        )
        if settings.DEBUG:
            print(f"Subscription Error: {e}")
        return redirect('memorials:index')


@require_http_methods(["GET", "POST"])
def unsubscribe(request, email):
    """
    Handle newsletter unsubscription requests.
    
    GET: Shows confirmation page
    POST: Processes unsubscription
    """
    try:
        subscriber = Subscriber.objects.get(email=email)

        if request.method == 'POST':
            subscriber.subscribed = False
            subscriber.save()
            messages.success(
                request,
                'You have been unsubscribed from our newsletter.'
            )
            return redirect('memorials:index')

        # Show confirmation page for GET requests
        return render(
            request,
            'newsletter/unsubscribe_confirm.html',
            {'email': email}
        )

    except Subscriber.DoesNotExist:
        messages.error(request, 'This email is not subscribed.')
        return redirect('memorials:index')