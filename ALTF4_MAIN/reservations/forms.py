from django import forms
from .models import Reservation
from labs.models import Equipment
from django.db.models import Q
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

    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.none(), 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox h-4 w-4 text-indigo-600 transition duration-150 ease-in-out'}),
        required=False,
        label="Select Equipment Required"
    )

    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'duration', 'equipment', 'purpose']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full'}),
            'purpose': forms.Textarea(attrs={
                'class': 'border p-2 rounded w-full', 
                'rows': 3, 
                'placeholder': 'Briefly describe your experiment or reason for booking...'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract lab and user from kwargs
        self.lab = kwargs.pop('lab', None)
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if self.lab:
            self.fields['equipment'].queryset = Equipment.objects.filter(
                lab=self.lab, 
                is_operational=True
            )

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration')
        selected_equipment = cleaned_data.get('equipment')
        
        # 1. Weekend Validation
        if booking_date and booking_date.weekday() >= 5:
            raise forms.ValidationError("Laboratories are closed on weekends. Please choose a weekday (Monday - Friday).")

        # 2. Past Date/Time Validation
        if booking_date:
            if booking_date < date.today():
                raise forms.ValidationError("You cannot book a date in the past.")
            
            if booking_date == date.today() and start_time:
                if start_time < datetime.now().time():
                    raise forms.ValidationError("You cannot book a time slot that has already passed today.")

        # 3. Calculate End Time
        if start_time and duration:
            duration_minutes = int(duration)
            reference_date = booking_date if booking_date else date.today()
            start_dt = datetime.combine(reference_date, start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            if end_dt.date() > reference_date:
                 raise forms.ValidationError("Reservations cannot extend past midnight.")
            
            end_time = end_dt.time()
            cleaned_data['end_time'] = end_time

            # 4. User Schedule Conflict Check (New)
            if self.user and booking_date:
                user_conflicts = Reservation.objects.filter(
                    user=self.user,
                    date=booking_date
                ).exclude(
                    status='REJECTED' # Ignore rejected, but count PENDING and CONFIRMED
                ).filter(
                    Q(start_time__lt=end_time) & 
                    Q(end_time__gt=start_time)
                )
                
                # Exclude current reservation if editing
                if self.instance.pk:
                    user_conflicts = user_conflicts.exclude(pk=self.instance.pk)

                if user_conflicts.exists():
                    raise forms.ValidationError("You already have another reservation during this time slot. Please choose a different time.")

            # 5. Equipment Availability Check
            if selected_equipment and self.lab and booking_date:
                overlapping_reservations = Reservation.objects.filter(
                    lab=self.lab,
                    date=booking_date
                ).exclude(
                    status='REJECTED'
                ).filter(
                    Q(start_time__lt=end_time) & 
                    Q(end_time__gt=start_time)
                )

                if self.instance.pk:
                    overlapping_reservations = overlapping_reservations.exclude(pk=self.instance.pk)

                unavailable_items = []
                for item in selected_equipment:
                    if overlapping_reservations.filter(equipment=item).exists():
                        unavailable_items.append(item.name)
                
                if unavailable_items:
                    items_str = ", ".join(unavailable_items)
                    raise forms.ValidationError(f"The following equipment is already booked for this time slot: {items_str}. Please choose a different time or equipment.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Re-calculate end_time for saving (in case clean wasn't called or for safety)
        if 'start_time' in self.cleaned_data and 'duration' in self.cleaned_data:
            start_time = self.cleaned_data['start_time']
            duration_minutes = int(self.cleaned_data['duration'])
            dummy_date = date.today()
            start_dt = datetime.combine(dummy_date, start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            instance.end_time = end_dt.time()
        
        if commit:
            instance.save()
            self.save_m2m()
            
        return instance