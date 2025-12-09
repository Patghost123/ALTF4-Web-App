from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.utils import timezone 
from reservations.models import Reservation
from labs.models import Lab, Equipment
from datetime import timedelta 
from reservations.models import Reservation
from labs.models import Lab, Equipment
from django.utils import timezone
from datetime import datetime

def is_staff(user):
    return user.is_staff

@login_required 
@user_passes_test(is_staff)
def dashboard(request):
    # Define the rolling 30-day period for booking stats
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    # FIX: Define the 60-day backlog threshold date for maintenance
    sixty_days_ago = timezone.now().date() - timedelta(days=60) # <--- ADDED DEFINITION HERE

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


    # --- 2. Stats & Bookings (Rolling 30-Day Period) ---
    recent_reservations = Reservation.objects.filter(date__gte=thirty_days_ago)

    lab_stats = recent_reservations.values('lab__name').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    user_stats = recent_reservations.values('user__username', 'user__email').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    total_reservations = recent_reservations.count() 
    total_labs = Lab.objects.filter(is_active=True).count()

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


    # --- 3. RESOURCE GAP ANALYSIS (FIXED) ---
    resource_gaps = []
    
    # Annotate labs with equipment counts AND overdue counts
    labs_data = Lab.objects.annotate(
        total_eq=Count('equipment'),
        operational_eq=Count('equipment', filter=Q(equipment__is_operational=True)),
        broken_eq=Count('equipment', filter=Q(equipment__is_operational=False)),
        
        # FIX: Ensure we only count equipment where last_maintenance is NOT NULL, 
        # and its date is less than sixty_days_ago.
        backlog_eq=Count('equipment', 
                         filter=Q(equipment__last_maintenance__isnull=False) & 
                                Q(equipment__last_maintenance__lt=sixty_days_ago)
                        )
    )
    
    # Calculate 30-day booking counts separately and merge
    monthly_bookings = recent_reservations.values('lab__id').annotate(
        booking_count=Count('id')
    )
    monthly_booking_map = {item['lab__id']: item['booking_count'] for item in monthly_bookings}


    for lab in labs_data:
        gaps_found = []
        
        # Get 30-day booking count
        booking_count = monthly_booking_map.get(lab.id, 0)

        # Safety check: Avoid division by zero
        if lab.total_eq > 0:
            broken_pct = (lab.broken_eq / lab.total_eq) * 100
            backlog_pct = (lab.backlog_eq / lab.total_eq) * 100 
            
            # 3A. Check Critical Maintenance Gap (Broken Equipment)
            if broken_pct >= maintenance_threshold:
                gaps_found.append({
                    'type': 'Critical Maintenance',
                    'message': f"{round(broken_pct, 1)}% of equipment is broken ({lab.broken_eq}/{lab.total_eq} items).",
                    'severity': 'high'
                })

            # 3B. Check Maintenance Backlog Gap 
            if backlog_pct >= maintenance_backlog_threshold:
                gaps_found.append({
                    'type': 'Maintenance Backlog',
                    'message': f"{round(backlog_pct, 1)}% of equipment ({lab.backlog_eq}/{lab.total_eq} items) is overdue for maintenance (> 60 days).",
                    'severity': 'medium'
                })
        
        # 3C. Check Equipment Density Gap
        if lab.capacity > 0 and lab.operational_eq > 0:
            density = lab.operational_eq / lab.capacity
            if density < density_threshold:
                gaps_found.append({
                    'type': 'Equipment Density',
                    'message': f"Low ratio ({round(density, 2)}). Only {lab.operational_eq} operational items for {lab.capacity} capacity.",
                    'severity': 'medium'
                })

        # 3D. Check Utilization Gaps (Over/Under)
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


        # If any gaps were found, add to the list
        if gaps_found:
            resource_gaps.append({
                'lab_name': lab.name,
                'issues': gaps_found
            })

    context = {
        'lab_stats': lab_stats,
        'user_stats': user_stats,
        'equipment_stats': equipment_stats,
        'total_reservations': total_reservations,
        'total_labs': total_labs,
        'resource_gaps': resource_gaps,
        'maintenance_threshold': maintenance_threshold,
        'booking_threshold': booking_threshold,
        'under_utilization_threshold': under_utilization_threshold,
        'density_threshold': density_threshold,
        'maintenance_backlog_threshold': maintenance_backlog_threshold,
        'start_date': start_date,
        'end_date': end_date,
        'all_labs': all_labs,
        'selected_lab_id': int(selected_lab_id) if selected_lab_id else None,
    }
    return render(request, 'analytics/dashboard.html', context)