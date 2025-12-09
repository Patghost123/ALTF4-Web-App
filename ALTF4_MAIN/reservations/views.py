from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .forms import ReservationForm
from .models import Reservation
from labs.models import Lab

# Check if user is staff (admin)
def is_staff(user):
    return user.is_staff

@login_required 
@user_passes_test(is_staff) # Restrict to Admins only
def admin_dashboard(request):
    # Handle POST actions (Approve/Reject)
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        action = request.POST.get('action')
        reservation = get_object_or_404(Reservation, id=reservation_id)

        if action == 'approve':
            reservation.status = 'CONFIRMED'
            reservation.save()
        elif action == 'reject':
            reason = request.POST.get('rejection_reason')
            reservation.status = 'REJECTED'
            reservation.rejection_reason = reason
            reservation.save()
        
        return redirect('reservations:dashboard')

    # Fetch data for dashboard
    pending_reservations = Reservation.objects.filter(status='PENDING').order_by('date')
    approved_reservations = Reservation.objects.filter(status='CONFIRMED').order_by('-date')[:10] # Show last 10
    
    context = {
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations
    }
    return render(request, 'reservations/admin_dashboard.html', context)

@login_required
def my_reservations(request):
    """ View for users to see their own reservation history and status """
    # Fetch reservations for the logged-in user, newest first
    reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-start_time')
    
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})

# ... [Existing User Views Below] ...

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
                form.add_error(None, "This time slot is already booked or pending approval.")
            else:
                reservation.save()
                return redirect('reservations:success')
    else:
        form = ReservationForm(initial=initial_data)

    bookings = Reservation.objects.filter(
        lab=lab,
        date__gte=timezone.now().date()
    ).exclude(status='REJECTED').order_by('date', 'start_time')
        
    return render(request, 'reservations/reserve.html', {'form': form, 'bookings': bookings, 'lab': lab})

@login_required 
def reservation_success(request):
    return render(request, 'reservations/success.html')

@login_required 
def timetable(request):
    labs = Lab.objects.filter(is_active=True)
    selected_lab_id = request.GET.get('lab')
    context = {
        'labs': labs,
        'selected_lab_id': int(selected_lab_id) if selected_lab_id else None
    }
    return render(request, 'reservations/timetable.html', context)

def all_reservations_api(request):
    reservations = Reservation.objects.exclude(status='REJECTED')
    lab_id = request.GET.get('lab_id')
    if lab_id:
        reservations = reservations.filter(lab_id=lab_id)

    events = []
    for res in reservations:
        if not lab_id:
            base_title = f"{res.lab.name} ({res.user.username})"
        else:
            base_title = res.user.username

        if res.status == 'CONFIRMED':
            bg_color = '#16a34a'
            border_color = '#16a34a'
            title = base_title
        else:
            bg_color = '#f59e0b'
            border_color = '#f59e0b'
            title = f"{base_title} (Pending)"

        events.append({
            'title': title,
            'start': f"{res.date}T{res.start_time}",
            'end': f"{res.date}T{res.end_time}",
            'backgroundColor': bg_color, 
            'borderColor': border_color,
        })
    return JsonResponse(events, safe=False)