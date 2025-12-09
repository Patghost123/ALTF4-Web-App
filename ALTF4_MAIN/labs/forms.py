from django import forms
from django.forms.models import inlineformset_factory
from .models import Lab, Equipment

# --- 1. Base Form for Lab Details (No Change) ---
class LabForm(forms.ModelForm):
    # ... (Meta and widgets remain the same) ...
    class Meta:
        model = Lab
        fields = ['name', 'capacity', 'description', 'is_active', 'safety_guidelines']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
            'safety_guidelines': forms.Textarea(attrs={'rows': 6, 'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# --- Updated Form for Equipment Item ---
class EquipmentItemForm(forms.ModelForm):
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 border rounded', 
            'rows': 2, 
            'placeholder': 'Brief description...'
        })
    )

    class Meta:
        model = Equipment
        # ADDED 'quantity' to the fields list
        fields = ('name', 'serial_number', 'quantity', 'description', 'is_operational', 'last_maintenance')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Equipment Name'}),
            'serial_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'S/N'}),
            # NEW WIDGET: Quantity input
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Qty', 'min': 1}),
            'last_maintenance': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
        }

# --- Updated Formset for Equipment Management ---
EquipmentFormSet = inlineformset_factory(
    Lab,
    Equipment,
    form=EquipmentItemForm,
    # ADDED 'quantity' to the formset fields list
    fields=('name', 'serial_number', 'quantity', 'description', 'is_operational', 'last_maintenance'),
    extra=1,
    can_delete=True
)