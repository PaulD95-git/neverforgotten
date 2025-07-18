# plans/urls.py

from django.urls import path
from . import views

app_name = 'plans'

# URL patterns for the plans app
# These URLs handle plan selection, checkout sessions, payment success, cancellation,
urlpatterns = [
    path('choose/<int:memorial_id>/', views.choose_plan, name='choose_plan'),
    path('checkout/<int:plan_id>/<int:memorial_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('cancel/<int:memorial_id>/', views.cancel_plan, name='cancel_plan'),
]