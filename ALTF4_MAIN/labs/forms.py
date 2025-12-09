from django import forms
from django.forms.models import inlineformset_factory
from .models import Lab, Equipment

# --- 1. Base Form for Lab Details ---
class LabForm(forms.ModelForm):
    """
    Form for updating the main Lab attributes (name, description, capacity, status, safety_guidelines).
    """
    class Meta:
        model = Lab
        # ADDED 'safety_guidelines' to the fields list
        fields = ['name', 'capacity', 'description', 'is_active', 'safety_guidelines'] 
        widgets = {
            # Use 'rows' attribute for Textareas to give them height
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
            'safety_guidelines': forms.Textarea(attrs={'rows': 6, 'class': 'w-full p-2 border rounded'}), # Added Widget
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
            'last_maintenance': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}), 
        }

# --- 2. Formset for Equipment Management ---
EquipmentFormSet = inlineformset_factory(
    Lab,
    Equipment,
    form=EquipmentItemForm,
    fields=('name', 'serial_number', 'is_operational', 'last_maintenance'),
    extra=1,
    can_delete=True
)