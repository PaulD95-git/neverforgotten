from django import forms
from .models import Memorial


# --- Memorial Form ---
class MemorialForm(forms.ModelForm):
    """Form for creating/editing memorial profiles."""
    class Meta:
        model = Memorial
        fields = [
            'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'date_of_death',
            'profile_picture', 'audio_file', 'quote'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'date_of_death': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }