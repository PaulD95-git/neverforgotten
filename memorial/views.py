# Django core imports
from django.shortcuts import (
    render, get_object_or_404, redirect, reverse
)
from django.views.generic import (
    ListView, CreateView, UpdateView, FormView, DetailView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


from django.contrib.auth.models import User
from django import forms


# Third-party imports

import cloudinary
import stripe


# Local imports
from plans.models import Plan
from .models import (
    Memorial,
)
from .forms import (
    MemorialForm, 
)

# ---------------------------
# Basic Views
# ---------------------------


def index(request):
    """Render the homepage"""
    return render(request, 'index.html')

# ---------------------------
# Memorial CRUD Views
# ---------------------------

class MemorialCreateView(LoginRequiredMixin, CreateView):
    """View for creating new memorials"""
    model = Memorial
    form_class = MemorialForm
    template_name = 'memorials/memorial_form.html'

    def form_valid(self, form):
        """Assign user and default free plan before saving"""
        form.instance.user = self.request.user
        
        try:
            free_plan = Plan.objects.get(name='free')
            form.instance.plan = free_plan
        except Plan.DoesNotExist:
            pass

        memorial = form.save()
        return redirect(reverse(
            'plans:choose_plan',
            kwargs={'memorial_id': memorial.pk}
        ))

class MemorialEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for editing existing memorials"""
    model = Memorial
    form_class = MemorialForm
    template_name = 'memorials/memorial_edit.html'

    def get_success_url(self):
        """Redirect to memorial detail after edit"""
        return reverse_lazy(
            'memorials:memorial_detail',
            kwargs={'pk': self.object.pk}
        )

    def test_func(self):
        """Ensure only memorial owner can edit"""
        return self.request.user == self.get_object().user

    def get_context_data(self, **kwargs):
        """Add update URLs to context"""
        context = super().get_context_data(**kwargs)
        context['update_name_url'] = reverse_lazy(
            'memorials:update_name',
            kwargs={'pk': self.object.pk}
        )
        context['update_dates_url'] = reverse_lazy(
            'memorials:update_dates',
            kwargs={'pk': self.object.pk}
        )
        return context

@login_required
def delete_memorial(request, pk):
    """View for deleting a memorial and its associated data"""
    memorial = get_object_or_404(Memorial, pk=pk, user=request.user)

    if request.method == "POST":
        if memorial.stripe_subscription_id:
            try:
                stripe.Subscription.delete(memorial.stripe_subscription_id)
            except stripe.error.StripeError as e:
                messages.error(
                    request,
                    "Error canceling subscription. Please try again."
                )
                return redirect('memorials:memorial_detail', pk=pk)
            except Exception as e:
                messages.warning(
                    request,
                    "Memorial deleted but subscription cancel failed."
                )
        
        memorial.delete()
        messages.success(request, "Memorial has been deleted.")
        return redirect('memorials:account_profile')

    return redirect('memorials:memorial_detail', pk=pk)

# ---------------------------
# Memorial Content Views
# ---------------------------

@csrf_protect
def memorial_detail(request, pk):
    """Detailed view of a memorial with tributes and stories"""
    memorial = get_object_or_404(Memorial, pk=pk)
    memorial.refresh_from_db()

    tributes = memorial.tributes.all().order_by('-created_at')[:6]
    stories = memorial.stories.all().order_by('-created_at')[:3]

    plan_name = memorial.plan.name.lower() if memorial.plan else ""
    is_premium_plan = plan_name in ['premium', 'lifetime']
    is_premium = (
        request.user.is_authenticated and
        request.user == memorial.user and
        is_premium_plan
    )

    if (request.method == 'POST' and
            request.headers.get('x-requested-with') == 'XMLHttpRequest'):
        if 'story_content' in request.POST:
            return create_story(request, pk)
        return create_tribute(request, pk)

    return render(
        request,
        'memorials/memorial_detail.html',
        {
            'memorial': memorial,
            'tributes': tributes,
            'stories': stories,
            'is_premium': is_premium,
            'request': request,
        }
    )


# ---------------------------
# Upgrade Views
# ---------------------------

class UpgradeMemorialForm(forms.Form):
    """Form for selecting a memorial upgrade plan"""
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.exclude(name__iexact='free'),
        empty_label=None,
        widget=forms.RadioSelect
    )

class UpgradeMemorialView(LoginRequiredMixin, FormView):
    """View for upgrading memorial plans"""
    template_name = 'memorials/upgrade_memorial.html'
    form_class = UpgradeMemorialForm

    def dispatch(self, request, *args, **kwargs):
        """Get memorial and check permissions"""
        self.memorial = get_object_or_404(
            Memorial,
            pk=kwargs['pk'],
            user=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle form submission for plan upgrade"""
        selected_plan = form.cleaned_data['plan']
        self.memorial.plan = selected_plan
        self.memorial.save()
        return redirect(reverse_lazy('memorials:my_account'))

    def get_context_data(self, **kwargs):
        """Add memorial to template context"""
        context = super().get_context_data(**kwargs)
        context['memorial'] = self.memorial
        return context
