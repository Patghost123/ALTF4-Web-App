from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .forms import ReservationForm
from .models import Reservation
from labs.models import Lab

# This decorator forces the user to login before running this function
@login_required 
def make_reservation(request):
    # Pre-select lab if passed in URL
    initial_data = {}
    if 'lab_id' in request.GET:
        initial_data['lab'] = request.GET['lab_id']

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user  # Now guaranteed to be a real user
            
            # Check for conflicts
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

    # --- NEW LOGIC: Fetch upcoming bookings for the side panel ---
    # This allows the template to loop through 'bookings' and show the table
    bookings = Reservation.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')
        
    return render(request, 'reservations/reserve.html', {'form': form, 'bookings': bookings})

def reservation_success(request):
    return render(request, 'reservations/success.html')

def lab_status_api(request):
    """ API for the map to see busy labs """
    now = timezone.now()
    active_reservations = Reservation.objects.filter(
        date=now.date(),
        start_time__lte=now.time(),
        end_time__gte=now.time()
    )
    busy_ids = [res.lab.map_svg_id for res in active_reservations]
    return JsonResponse({'occupied_ids': busy_ids})

def timetable(request):
    """ Display upcoming reservations (Standalone Page) """
    upcoming_reservations = Reservation.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')
    
    labs = Lab.objects.filter(is_active=True)
    selected_lab_id = request.GET.get('lab')
    
    if selected_lab_id:
        upcoming_reservations = upcoming_reservations.filter(lab_id=selected_lab_id)

    context = {
        'reservations': upcoming_reservations,
        'labs': labs,
        'selected_lab_id': int(selected_lab_id) if selected_lab_id else None
    }
    return render(request, 'reservations/timetable.html', context)  

