from django import forms
from .models import Memorial, Tribute, GalleryImage, Story


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


# --- Tribute Form ---
class TributeForm(forms.ModelForm):
    """Form for submitting tributes/memories."""
    class Meta:
        model = Tribute
        fields = ['author_name', 'message']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your tribute...'
            }),
        }
        labels = {
            'author_name': 'Your Name',
            'message': 'Tribute Message',
        }


# --- Gallery Image Form ---
class GalleryImageForm(forms.ModelForm):
    """Form for uploading memorial gallery images."""
    class Meta:
        model = GalleryImage
        fields = ['image', 'caption']


# --- Story Form ---
class StoryForm(forms.ModelForm):
    """Form for sharing longer memorial stories."""
    class Meta:
        model = Story
        fields = ['author_name', 'title', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Story Title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your story...'
            }),
        }
        labels = {
            'author_name': 'Your Name',
            'title': 'Story Title',
            'content': 'Your Story',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'minlength': '50'})