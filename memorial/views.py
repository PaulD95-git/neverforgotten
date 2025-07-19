# Standard Library
from datetime import datetime
from urllib.parse import urlencode
import json
from django.http import JsonResponse

# Django Imports
from django.views.decorators.http import require_POST

# Django Core
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, CreateView, UpdateView, FormView

# Third Party

import stripe


# Local Apps
from plans.models import Plan
from .forms import MemorialForm
from .models import Memorial


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



# memorial/views.py (add these at the bottom)

class MyAccountView(LoginRequiredMixin, ListView):
    """View showing user's memorials"""
    model = Memorial
    template_name = 'account/my_account.html'
    context_object_name = 'memorials'

    def get_queryset(self):
        """Filter memorials to only those owned by current user"""
        return Memorial.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Add free plan info to context"""
        context = super().get_context_data(**kwargs)
        free_plan = Plan.objects.filter(name__iexact='free').first()
        context['plans_free_plan'] = free_plan
        return context

class UserEditForm(forms.ModelForm):
    """Form for editing user profile information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

@login_required
def edit_profile(request):
    """View for editing user profile"""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('memorials:account_profile')  # Fixed URL name
    else:
        form = UserEditForm(instance=request.user)
    
    return render(
        request,
        'account/edit_profile.html',
        {'form': form}
    )


@require_POST
@login_required
def update_banner(request, pk):
    """AJAX endpoint for updating memorial banner"""
    try:
        memorial = Memorial.objects.get(pk=pk, user=request.user)
        
        banner_type = request.POST.get('banner_type')
        banner_value = request.POST.get('banner_value')
        
        if not banner_type or not banner_value:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)
        
        if banner_type not in ['image', 'color']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid banner type'
            }, status=400)
        
        if banner_type == 'image' and banner_value.startswith('/static/'):
            banner_value = banner_value.replace('/static/', '')
        
        memorial.banner_type = banner_type
        memorial.banner_value = banner_value
        memorial.save()
        
        return JsonResponse({
            'status': 'success',
            'banner_type': banner_type,
            'banner_value': banner_value
        })
        
    except Memorial.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Memorial not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@login_required
def upload_profile_picture(request, pk):
    """View for uploading profile pictures to Cloudinary"""
    memorial = get_object_or_404(Memorial, pk=pk, user=request.user)

    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile_pic = request.FILES['profile_picture']

        if profile_pic.size > 5 * 1024 * 1024:
            return JsonResponse(
                {'status': 'error', 'message': 'Image too large (max 5MB)'},
                status=400
            )

        if not profile_pic.content_type.startswith('image/'):
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid file type'},
                status=400
            )

        try:
            if memorial.profile_picture:
                memorial.profile_picture.delete()

            upload_result = upload(
                profile_pic,
                folder=f"memorials/{memorial.id}/profile_pictures",
                public_id=f"profile_{memorial.id}",
                overwrite=True,
                resource_type="image"
            )

            memorial.profile_public_id = upload_result['public_id']
            memorial.profile_picture.name = upload_result['public_id']
            memorial.save()

            return JsonResponse({
                'status': 'success',
                'profile_picture_url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'message': 'Profile picture updated!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }, status=500)

    return JsonResponse(
        {'status': 'error', 'message': 'Invalid request'},
        status=400
    )


@require_POST
def update_name(request, pk):
    """AJAX endpoint for updating memorial name"""
    try:
        memorial = Memorial.objects.get(pk=pk)
        memorial.first_name = request.POST.get('first_name', '')
        memorial.middle_name = request.POST.get('middle_name', '')
        memorial.last_name = request.POST.get('last_name', '')
        memorial.save()
        
        full_name = (
            f"{memorial.first_name} "
            f"{memorial.middle_name + ' ' if memorial.middle_name else ''}"
            f"{memorial.last_name}"
        )
        
        return JsonResponse({
            'status': 'success',
            'new_name': full_name.strip()
        })
    except Memorial.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Memorial not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )

@require_POST
def update_dates(request, pk):
    """AJAX endpoint for updating memorial dates"""
    try:
        memorial = Memorial.objects.get(pk=pk)
        
        date_of_birth_str = request.POST.get('date_of_birth')
        date_of_death_str = request.POST.get('date_of_death')
        
        try:
            date_of_birth = datetime.strptime(
                date_of_birth_str,
                '%Y-%m-%d'
            ).date()
            date_of_death = datetime.strptime(
                date_of_death_str,
                '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid date format. Use YYYY-MM-DD.'
            }, status=400)
        
        memorial.date_of_birth = date_of_birth
        memorial.date_of_death = date_of_death
        memorial.save()
        
        return JsonResponse({
            'status': 'success',
            'new_dates': (
                f"{date_of_birth.strftime('%B %d, %Y')} - "
                f"{date_of_death.strftime('%B %d, %Y')}"
            )
        })
    except Memorial.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Memorial not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )

@require_POST
@login_required
def update_quote(request, pk):
    """AJAX endpoint for updating memorial quote"""
    memorial = get_object_or_404(Memorial, pk=pk, user=request.user)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quote = data.get('quote', '').strip()
        else:
            quote = request.POST.get('quote', '').strip()

        memorial.quote = quote
        memorial.save()

        return JsonResponse({
            'status': 'success',
            'quote': memorial.quote,
            'message': 'Quote updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
@login_required
def update_biography(request, pk):
    """AJAX endpoint for updating memorial biography"""
    try:
        memorial = get_object_or_404(Memorial, pk=pk, user=request.user)
        biography = request.POST.get('biography', '')
        memorial.biography = biography
        memorial.save()
        return JsonResponse({
            'success': True,
            'biography': biography.replace('\n', '<br>')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)