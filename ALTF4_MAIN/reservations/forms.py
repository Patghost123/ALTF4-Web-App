from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        # CHANGED: 'room' is replaced by 'lab' to match your new model
        fields = ['lab', 'date', 'start_time', 'end_time']
        
        # Widgets to make the form look nice with Date/Time pickers
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border p-2 rounded w-full'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border p-2 rounded w-full'}),
            'lab': forms.Select(attrs={'class': 'border p-2 rounded w-full'})
        }