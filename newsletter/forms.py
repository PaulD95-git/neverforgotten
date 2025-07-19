# newsletter/forms.py
from django import forms
from .models import Subscriber


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name (optional)'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name (optional)'}),
        }
