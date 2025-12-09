from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from reservations.models import Reservation
from labs.models import Lab, Equipment
from django.utils import timezone
from datetime import datetime

def is_staff(user):
    return user.is_staff

@login_required 
def dashboard(request):
    # --- Date & Lab Filtering Logic ---
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_lab_id = request.GET.get('lab_id')
    
    # Base Queryset
    reservations = Reservation.objects.all()

    # Apply Filters
    if start_date:
        reservations = reservations.filter(date__gte=start_date)
    if end_date:
        reservations = reservations.filter(date__lte=end_date)
    if selected_lab_id:
        reservations = reservations.filter(lab_id=selected_lab_id)

    # 1. Lab Usage Stats (Filtered)
    # If a specific lab is selected, this list will only have 1 item, which is fine.
    lab_stats = reservations.values('lab__name').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # 2. User Activity Stats (Filtered)
    user_stats = reservations.values('user__username', 'user__email').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # 3. Equipment Usage Stats (Filtered)
    # We need to filter based on the reservation date, so we filter the related reservations first
    # Also filter equipment by the selected lab if applicable
    equipment_qs = Equipment.objects.all()
    if selected_lab_id:
        equipment_qs = equipment_qs.filter(lab_id=selected_lab_id)

    equipment_stats = equipment_qs.annotate(
        total_uses=Count('reservations', filter=Q(reservations__in=reservations))
    ).order_by('-total_uses')

    # 4. Total stats (Filtered)
    total_reservations = reservations.count()
    
    # Active labs count might change if filtered? Usually "Total Active Labs" implies system-wide,
    # but in a report context, if we filter by 1 lab, maybe we show 1. 
    # Let's keep it system-wide for context, unless filtered.
    if selected_lab_id:
        total_labs = 1 
    else:
        total_labs = Lab.objects.filter(is_active=True).count()

    # Context Data
    # Fetch all labs for the dropdown
    all_labs = Lab.objects.filter(is_active=True)

    context = {
        'lab_stats': lab_stats,
        'user_stats': user_stats,
        'equipment_stats': equipment_stats,
        'total_reservations': total_reservations,
        'total_labs': total_labs,
        'start_date': start_date,
        'end_date': end_date,
        'all_labs': all_labs,
        'selected_lab_id': int(selected_lab_id) if selected_lab_id else None,
    }
    return render(request, 'analytics/dashboard.html', context)