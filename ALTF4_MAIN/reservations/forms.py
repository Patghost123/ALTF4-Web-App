# patghost123/altf4-web-app/ALTF4_MAIN/reservations/forms.py

from django import forms
from .models import Reservation
from datetime import timedelta, datetime, date, time

def generate_time_choices():
    """Generates 30-minute intervals from 8:00 AM to 8:00 PM"""
    choices = []
    for hour in range(8, 20): 
        for minute in (0, 30):
            t = time(hour, minute)
            display = t.strftime('%I:%M %p')
            value = t.strftime('%H:%M')
            choices.append((value, display))
    return choices

class ReservationForm(forms.ModelForm):
    DURATION_CHOICES = [
        (30, '30 Minutes'),
        (60, '1 Hour'),
        (90, '1 Hour 30 Minutes'),
        (120, '2 Hours'),
        (150, '2 Hours 30 Minutes'),
        (180, '3 Hours'),
        (210, '3 Hours 30 Minutes'),
        (240, '4 Hours'),
    ]

    start_time = forms.TimeField(
        widget=forms.Select(
            choices=generate_time_choices(),
            attrs={'class': 'border p-2 rounded w-full'}
        ),
        label="Start Time"
    )
    
    duration = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        label="Duration",
        widget=forms.Select(attrs={'class': 'border p-2 rounded w-full'})
    )

    class Meta:
        model = Reservation
        # CHANGED: Removed 'lab' from fields
        fields = ['date', 'start_time']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration')
        
        # 1. Weekend Validation
        if booking_date and booking_date.weekday() >= 5:
            raise forms.ValidationError("Laboratories are closed on weekends. Please choose a weekday (Monday - Friday).")

        # 2. Past Date/Time Validation
        if booking_date:
            # Check if the date is in the past
            if booking_date < date.today():
                raise forms.ValidationError("You cannot book a date in the past.")
            
            # If the booking is for today, ensure the time hasn't passed yet
            if booking_date == date.today() and start_time:
                # We use datetime.now().time() to get the current system time
                if start_time < datetime.now().time():
                    raise forms.ValidationError("You cannot book a time slot that has already passed today.")

        if start_time and duration:
            duration_minutes = int(duration)
            reference_date = booking_date if booking_date else date.today()
            start_dt = datetime.combine(reference_date, start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            if end_dt.date() > reference_date:
                 raise forms.ValidationError("Reservations cannot extend past midnight.")
                 
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        start_time = self.cleaned_data['start_time']
        duration_minutes = int(self.cleaned_data['duration'])
        
        dummy_date = date.today()
        start_dt = datetime.combine(dummy_date, start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        instance.end_time = end_dt.time()
        
        if commit:
            instance.save()
        return instance