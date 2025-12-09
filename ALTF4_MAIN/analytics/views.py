from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from reservations.models import Reservation
from labs.models import Lab

def is_staff(user):
    return user.is_staff

@login_required 

def dashboard(request):
    # 1. Lab Usage Stats
    # Groups by 'lab' and counts the number of reservations
    lab_stats = Reservation.objects.values('lab__name').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # 2. User Activity Stats
    # Groups by 'user' and counts their reservations
    user_stats = Reservation.objects.values('user__username', 'user__email').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')

    # 3. Total stats
    total_reservations = Reservation.objects.count()
    total_labs = Lab.objects.filter(is_active=True).count()

    context = {
        'lab_stats': lab_stats,
        'user_stats': user_stats,
        'total_reservations': total_reservations,
        'total_labs': total_labs
    }
    return render(request, 'analytics/dashboard.html', context)