from django import forms
from project.models import Movie, WatchHistory, Category

class MovieForm(forms.ModelForm):
    """
    Form for creating or updating movies.
    Used by admins or staff users.
    """
    class Meta:
        model = Movie
        fields = [
            'title',
            'category',
            'description',
            'release_year',
            'duration_minutes',
            'thumbnail',
            'video_file',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter movie title',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter a short description',
            }),
            'release_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Year',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 120',
            }),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration <= 0:
            raise forms.ValidationError("Duration must be greater than 0 minutes.")
        return duration


class WatchProgressForm(forms.ModelForm):
    """
    Form for updating a user's watched progress (in minutes).
    """
    class Meta:
        model = WatchHistory
        fields = ['watched_minutes']
        widgets = {
            'watched_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter minutes watched',
                'min': 0,
            })
        }

    def clean_watched_minutes(self):
        watched_minutes = self.cleaned_data.get('watched_minutes')
        if watched_minutes < 0:
            raise forms.ValidationError("Watched minutes cannot be negative.")
        return watched_minutes


class MovieFilterForm(forms.Form):
    """
    Optional: Simple form to filter movies by category or search keyword.
    """
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title...',
        })
    )
