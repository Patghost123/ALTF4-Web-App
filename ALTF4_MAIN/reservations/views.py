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
            reservation.lab = lab
            # Status defaults to PENDING via model, so we don't need to set it explicitly here
            
            # Conflict Check: Exclude REJECTED reservations from blocking the slot
            conflicts = Reservation.objects.filter(
                lab=reservation.lab,
                date=reservation.date
            ).exclude(
                status='REJECTED'
            ).filter(
                Q(start_time__lt=reservation.end_time) & 
                Q(end_time__gt=reservation.start_time)
            )

            if conflicts.exists():
                # Optional: Check if the user is double booking themselves
                # user_conflicts = conflicts.filter(user=request.user)
                form.add_error(None, "This time slot is already booked or pending approval.")
            else:
                reservation.save()
                return redirect('reservations:success')
    else:
        form = ReservationForm(initial=initial_data)

    # Sidebar List: Exclude Rejected items
    bookings = Reservation.objects.filter(
        lab=lab,
        date__gte=timezone.now().date()
    ).exclude(status='REJECTED').order_by('date', 'start_time')
        
    return render(request, 'reservations/reserve.html', {'form': form, 'bookings': bookings, 'lab': lab})

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
    # API: Exclude REJECTED reservations so they don't appear on calendar
    reservations = Reservation.objects.exclude(status='REJECTED')
    
    lab_id = request.GET.get('lab_id')
    if lab_id:
        reservations = reservations.filter(lab_id=lab_id)

    events = []
    for res in reservations:
        # Color coding: Green for Confirmed, Amber/Orange for Pending
        if res.status == 'CONFIRMED':
            bg_color = '#16a34a' # Green
            border_color = '#16a34a'
            title = f"{res.user.username}"
        else:
            bg_color = '#f59e0b' # Amber/Orange
            border_color = '#f59e0b'
            title = f"{res.user.username} (Pending)"

        events.append({
            'title': title,
            'start': f"{res.date}T{res.start_time}",
            'end': f"{res.date}T{res.end_time}",
            'backgroundColor': bg_color, 
            'borderColor': border_color,
        })
    return JsonResponse(events, safe=False)