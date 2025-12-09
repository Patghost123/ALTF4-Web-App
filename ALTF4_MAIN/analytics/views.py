from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Sum # Import Sum
from django.utils import timezone 
from reservations.models import Reservation
from labs.models import Lab, Equipment # Assuming ReservationEquipment is imported via reservations.models
from datetime import timedelta, datetime
# Assuming ReservationEquipment is available in the context via an intermediate model, 
# but we will rely on Sum annotation on the related Equipment model.

def is_staff(user):
    return user.is_staff

@login_required 
@user_passes_test(is_staff)
def dashboard(request):
    # Define time period for checks
    sixty_days_ago = timezone.now().date() - timedelta(days=60)

    # --- 1. Get Thresholds from User Input ---
    
    raw_maintenance_threshold = request.GET.get('maintenance_threshold')
    raw_booking_threshold = request.GET.get('booking_threshold')
    raw_under_utilization_threshold = request.GET.get('under_utilization_threshold')
    raw_backlog_threshold = request.GET.get('maintenance_backlog_threshold')
    raw_density_threshold = request.GET.get('density_threshold')

    # Define a default value for fallbacks
    DEFAULT_MAINTENANCE = 20
    DEFAULT_BOOKING = 50
    DEFAULT_UNDER_UTILIZATION = 5
    DEFAULT_BACKLOG = 50
    DEFAULT_DENSITY = 0.15

    # Helper function to convert raw input, defaulting if empty or invalid
    def safe_convert(raw_value, default_value, type_func=int):
        if raw_value is None or raw_value.strip() == "":
            return default_value
        try:
            return type_func(raw_value)
        except ValueError:
            return default_value

    maintenance_threshold = safe_convert(raw_maintenance_threshold, DEFAULT_MAINTENANCE)
    booking_threshold = safe_convert(raw_booking_threshold, DEFAULT_BOOKING)
    under_utilization_threshold = safe_convert(raw_under_utilization_threshold, DEFAULT_UNDER_UTILIZATION)
    maintenance_backlog_threshold = safe_convert(raw_backlog_threshold, DEFAULT_BACKLOG)
    density_threshold = safe_convert(raw_density_threshold, DEFAULT_DENSITY, type_func=float)

    # --- 2. Date and Lab Filtering Logic (Applies to main stats tables) ---
    start_date_raw = request.GET.get('start_date')
    end_date_raw = request.GET.get('end_date')
    selected_lab_id_raw = request.GET.get('lab_id') # Renamed to prevent conflict with converted variable
    
    # Base Queryset
    reservations = Reservation.objects.all()

    # Apply Filters (Date and Lab)
    if start_date_raw:
        try:
            start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
            reservations = reservations.filter(date__gte=start_date)
        except ValueError:
            start_date = None
    else:
        start_date = None

    if end_date_raw:
        try:
            end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
            reservations = reservations.filter(date__lte=end_date)
        except ValueError:
            end_date = None
    else:
        end_date = None
        
    selected_lab_id = None
    if selected_lab_id_raw:
        try:
            selected_lab_id = int(selected_lab_id_raw)
            reservations = reservations.filter(lab_id=selected_lab_id)
        except ValueError:
            selected_lab_id = None


    # --- 3. Filtered Stats Calculation ---

    # Lab Usage Stats (Filtered by date range & selected lab)
    lab_stats = reservations.values('lab__name').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # User Activity Stats (Filtered)
    user_stats = reservations.values('user__username', 'user__email').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # Equipment Usage Stats (Filtered)
    equipment_qs = Equipment.objects.all()
    if selected_lab_id:
        equipment_qs = equipment_qs.filter(lab_id=selected_lab_id)

    # Note: Using Reservation.objects.all() as the base is required for the Count filter
    equipment_stats = equipment_qs.annotate(
        total_uses=Count('reservations', filter=Q(reservations__in=reservations)) 
    ).order_by('-total_uses')

    # Total stats (Filtered)
    total_reservations = reservations.count()
    
    if selected_lab_id:
        total_labs = 1 
    else:
        total_labs = Lab.objects.filter(is_active=True).count()


    # --- 4. RESOURCE GAP ANALYSIS (FIXED DENSITY TO USE QUANTITY SUM) ---
    resource_gaps = []
    
    # Reservations for the fixed 30-day utilization check
    recent_reservations_30days = Reservation.objects.filter(date__gte=timezone.now().date() - timedelta(days=30))
    
    # Annotate labs with equipment counts AND total OPERATIONAL quantity (FIXED)
    labs_data = Lab.objects.annotate(
        total_eq=Count('equipment'),
        broken_eq=Count('equipment', filter=Q(equipment__is_operational=False)),
        backlog_eq=Count('equipment', 
                         filter=Q(equipment__last_maintenance__isnull=False) & 
                                Q(equipment__last_maintenance__lt=sixty_days_ago)
                        ),
        # FIX: Calculate total QUANTITY of OPERATIONAL equipment
        total_operational_quantity=Sum('equipment__quantity', filter=Q(equipment__is_operational=True))
    ).order_by('name')
    
    # Calculate 30-day booking counts separately and merge
    monthly_bookings_map = {
        item['lab__id']: item['booking_count'] 
        for item in recent_reservations_30days.values('lab__id').annotate(booking_count=Count('id'))
    }


    for lab in labs_data:
        # If a specific lab is selected, only run gap analysis for that lab
        if selected_lab_id is not None and lab.id != selected_lab_id:
            continue

        gaps_found = []
        booking_count = monthly_bookings_map.get(lab.id, 0)
        
        # FIX: Get the calculated total operational quantity
        operational_quantity = lab.total_operational_quantity if lab.total_operational_quantity is not None else 0

        # Safety check: Avoid division by zero
        if lab.total_eq > 0:
            broken_pct = (lab.broken_eq / lab.total_eq) * 100
            backlog_pct = (lab.backlog_eq / lab.total_eq) * 100 
            
            # 4A. Critical Maintenance Gap
            if broken_pct >= maintenance_threshold:
                gaps_found.append({
                    'type': 'Critical Maintenance',
                    'message': f"{round(broken_pct, 1)}% of equipment is broken ({lab.broken_eq}/{lab.total_eq} records).", # Changed to records for clarity
                    'severity': 'high'
                })

            # 4B. Maintenance Backlog Gap 
            if backlog_pct >= maintenance_backlog_threshold:
                gaps_found.append({
                    'type': 'Maintenance Backlog',
                    'message': f"{round(backlog_pct, 1)}% of equipment records ({lab.backlog_eq}/{lab.total_eq}) is overdue for maintenance (> 60 days).",
                    'severity': 'medium'
                })
        
        # 4C. Check Equipment Density Gap (FIXED TO USE QUANTITY)
        if lab.capacity > 0 and operational_quantity > 0:
            density = operational_quantity / lab.capacity
            if density < density_threshold:
                gaps_found.append({
                    'type': 'Equipment Density',
                    'message': f"Low ratio ({round(density, 2)}). Only {operational_quantity} operational units available for {lab.capacity} capacity.",
                    'severity': 'medium'
                })

        # 4D. Check Utilization Gaps (Over/Under - uses 30-day count)
        if booking_count >= booking_threshold:
            gaps_found.append({
                'type': 'Over-Utilization',
                'message': f"High demand: {booking_count} bookings in the last 30 days. Consider adding capacity.",
                'severity': 'high'
            })
        elif booking_count <= under_utilization_threshold:
             gaps_found.append({
                'type': 'Under-Utilization',
                'message': f"Low demand: Only {booking_count} bookings in the last 30 days. Review lab visibility or relevance.",
                'severity': 'low'
            })

        if gaps_found:
            resource_gaps.append({
                'lab_name': lab.name,
                'issues': gaps_found
            })


    # Context Data
    all_labs = Lab.objects.filter(is_active=True)

    context = {
        'lab_stats': lab_stats,
        'user_stats': user_stats,
        'equipment_stats': equipment_stats,
        'total_reservations': total_reservations,
        'total_labs': total_labs,
        'resource_gaps': resource_gaps,
        
        # Thresholds passed to maintain form state
        'maintenance_threshold': maintenance_threshold,
        'booking_threshold': booking_threshold,
        'under_utilization_threshold': under_utilization_threshold,
        'density_threshold': density_threshold,
        'maintenance_backlog_threshold': maintenance_backlog_threshold,
        
        # Filtering variables passed to maintain form state
        'start_date': start_date_raw,
        'end_date': end_date_raw,
        'all_labs': all_labs,
        'selected_lab_id': selected_lab_id,
    }
    return render(request, 'analytics/dashboard.html', context)