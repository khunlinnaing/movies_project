from django import forms
from project.models import Category

class CategoryForm(forms.ModelForm):
    """
    Form for creating or editing movie categories.
    Example: Action, Comedy, Horror, Drama.
    """
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if not name:
            raise forms.ValidationError("Category name cannot be empty.")
        return name