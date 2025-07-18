from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from .models import Memorial
from plans.models import Plan
from .forms import MemorialForm


def index(request):
    """
    Render the index page of the memorial app.
    """
    return render(request, 'index.html')


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