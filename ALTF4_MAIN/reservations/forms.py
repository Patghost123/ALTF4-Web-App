from django import forms
from .models import Reservation, ReservationEquipment
from labs.models import Equipment
from django.db.models import Q, Sum
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

    # We keep this to allow the form to validate *which* items are selected, 
    # but we will manually handle quantity validation in clean()
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.none(), 
        required=False,
        widget=forms.CheckboxSelectMultiple(),
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

            # 4. User Schedule Conflict Check
            if self.user and booking_date:
                user_conflicts = Reservation.objects.filter(
                    user=self.user,
                    date=booking_date
                ).exclude(
                    status='REJECTED'
                ).filter(
                    Q(start_time__lt=end_time) & 
                    Q(end_time__gt=start_time)
                )
                
                if self.instance.pk:
                    user_conflicts = user_conflicts.exclude(pk=self.instance.pk)

                if user_conflicts.exists():
                    raise forms.ValidationError("You already have another reservation during this time slot. Please choose a different time.")

            # 5. Equipment Availability & Quantity Check
            if selected_equipment and self.lab and booking_date:
                # Find overlapping reservations
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
                self.cleaned_quantities = {} # Store for save()

                for item in selected_equipment:
                    # Get Requested Quantity from POST data
                    qty_key = f'quantity_{item.id}'
                    try:
                        requested_qty = int(self.data.get(qty_key, 1))
                    except (ValueError, TypeError):
                        requested_qty = 1
                    
                    if requested_qty < 1:
                        raise forms.ValidationError(f"Invalid quantity for {item.name}.")
                    
                    # Store validated quantity
                    self.cleaned_quantities[item.id] = requested_qty

                    # Check Inventory Cap
                    if requested_qty > item.quantity:
                        raise forms.ValidationError(f"You requested {requested_qty} {item.name}(s), but the lab only has {item.quantity} in total.")

                    # Check Overlapping Usage
                    used_qty = ReservationEquipment.objects.filter(
                        reservation__in=overlapping_reservations,
                        equipment=item
                    ).aggregate(total=Sum('quantity'))['total'] or 0
                    
                    remaining_qty = item.quantity - used_qty
                    
                    if requested_qty > remaining_qty:
                        unavailable_items.append(f"{item.name} (Requested: {requested_qty}, Available: {remaining_qty})")
                
                if unavailable_items:
                    items_str = ", ".join(unavailable_items)
                    raise forms.ValidationError(f"Insufficient equipment availability for this time slot: {items_str}. Please reduce quantity or choose a different time.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Ensure end_time is set
        if 'end_time' in self.cleaned_data:
            instance.end_time = self.cleaned_data['end_time']
        
        if commit:
            instance.save()
            # Handle M2M manually with quantities
            self.save_equipment(instance)
            
        return instance

    def save_equipment(self, reservation):
        """Helper to save ReservationEquipment with quantities"""
        # Clear existing equipment if updating
        reservation.reservationequipment_set.all().delete()
        
        selected_equipment = self.cleaned_data.get('equipment', [])
        for item in selected_equipment:
            qty = self.cleaned_quantities.get(item.id, 1)
            ReservationEquipment.objects.create(
                reservation=reservation,
                equipment=item,
                quantity=qty
            )
    
    # Override save_m2m to do nothing, as we handle it in save_equipment
    def save_m2m(self):
        pass