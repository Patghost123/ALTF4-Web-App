# patghost123/altf4-web-app/ALTF4_MAIN/reservations/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .forms import ReservationForm
from .models import Reservation
from labs.models import Lab

@login_required 
def make_reservation(request, lab_id):
    # 1. Fetch the specific lab by ID from the URL
    lab = get_object_or_404(Lab, pk=lab_id)
    
    initial_data = {}
    if 'date' in request.GET:
        initial_data['date'] = request.GET['date']
    if 'start_time' in request.GET:
        initial_data['start_time'] = request.GET['start_time']

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            # 2. Explicitly assign the lab from the URL
            reservation.lab = lab  
            
            # Conflict Check
            conflicts = Reservation.objects.filter(
                lab=reservation.lab,
                date=reservation.date
            ).filter(
                Q(start_time__lt=reservation.end_time) & 
                Q(end_time__gt=reservation.start_time)
            )

            if conflicts.exists():
                form.add_error(None, "This time slot is already booked for this lab.")
            else:
                reservation.save()
                return redirect('reservations:success')
    else:
        form = ReservationForm(initial=initial_data)

    # Filter sidebar bookings to show ONLY this lab's schedule
    bookings = Reservation.objects.filter(
        lab=lab,
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')
        
    return render(request, 'reservations/reserve.html', {'form': form, 'bookings': bookings, 'lab': lab})

# ... [Keep reservation_success, timetable, and api views unchanged] ...
def reservation_success(request):
    return render(request, 'reservations/success.html')

def timetable(request):
    labs = Lab.objects.filter(is_active=True)
    selected_lab_id = request.GET.get('lab')
    context = {
        'labs': labs,
        'selected_lab_id': int(selected_lab_id) if selected_lab_id else None
    }
    return render(request, 'reservations/timetable.html', context)

def all_reservations_api(request):
    reservations = Reservation.objects.all()
    lab_id = request.GET.get('lab_id')
    if lab_id:
        reservations = reservations.filter(lab_id=lab_id)

    events = []
    for res in reservations:
        events.append({
            'title': f"{res.user.username} - {res.lab.name}",
            'start': f"{res.date}T{res.start_time}",
            'end': f"{res.date}T{res.end_time}",
            'backgroundColor': '#4f46e5' if not lab_id else '#16a34a', 
            'borderColor': '#4f46e5' if not lab_id else '#16a34a',
        })
    return JsonResponse(events, safe=False)