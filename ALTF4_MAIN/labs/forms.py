from django import forms
from django.forms.models import inlineformset_factory
from .models import Lab, Equipment

# --- 1. Base Form for Lab Details ---
class LabForm(forms.ModelForm):
    """
    Form for updating the main Lab attributes (name, description, capacity, status).
    """
    class Meta:
        model = Lab
        fields = ['name', 'capacity', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# --- Form for Equipment Item (used in Formset) ---
class EquipmentItemForm(forms.ModelForm):
    """
    Custom form used in the formset to apply widgets and simplify field rendering.
    """
    class Meta:
        model = Equipment
        fields = ('name', 'serial_number', 'is_operational', 'last_maintenance')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'serial_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            # FIX: Use DateInput widget to render a calendar control
            'last_maintenance': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}), 
        }

# --- 2. Formset for Equipment Management ---
EquipmentFormSet = inlineformset_factory(
    Lab,
    Equipment,
    form=EquipmentItemForm, # Use the custom form definition
    fields=('name', 'serial_number', 'is_operational', 'last_maintenance'),
    extra=1,
    can_delete=True
)