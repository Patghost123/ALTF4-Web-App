from django import forms
from .models import Lab

class LabForm(forms.ModelForm):
    """
    ModelForm used for updating Lab attributes.
    Excludes 'slug' and 'map_svg_id' as these should generally not be changed 
    by standard administrators after creation.
    """
    class Meta:
        model = Lab
        fields = ['name', 'capacity', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }