from django import forms
from django.forms.models import inlineformset_factory
from .models import Lab, Equipment

# --- 1. Base Form for Lab Details ---
class LabForm(forms.ModelForm):
    """
    Form for updating the main Lab attributes.
    """
    class Meta:
        model = Lab
        fields = ['name', 'capacity', 'description', 'is_active', 'safety_guidelines']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
            'safety_guidelines': forms.Textarea(attrs={'rows': 6, 'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# --- Form for Equipment Item (used in Formset) ---
class EquipmentItemForm(forms.ModelForm):
    """
    Custom form used in the formset to apply widgets and simplify field rendering.
    """
    # 1. Explicitly define the field here to make it optional
    description = forms.CharField(
        required=False,  # <--- THIS FIXES THE ERROR
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 border rounded', 
            'rows': 2, 
            'placeholder': 'Brief description...'
        })
    )

    class Meta:
        model = Equipment
        fields = ('name', 'serial_number', 'description', 'is_operational', 'last_maintenance')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Equipment Name'}),
            'serial_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'S/N'}),
            # Note: 'description' widget is now defined above, so we can remove it from here
            'last_maintenance': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
        }

# --- 2. Formset for Equipment Management ---
EquipmentFormSet = inlineformset_factory(
    Lab,
    Equipment,
    form=EquipmentItemForm,
    # ADDED 'description' here as well
    fields=('name', 'serial_number', 'description', 'is_operational', 'last_maintenance'),
    extra=1,
    can_delete=True
)