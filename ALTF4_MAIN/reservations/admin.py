from django.contrib import admin
from .models import Reservation

@admin.action(description='Approve selected reservations')
def approve_reservations(modeladmin, request, queryset):
    queryset.update(status='CONFIRMED')

@admin.action(description='Reject selected reservations')
def reject_reservations(modeladmin, request, queryset):
    queryset.update(status='REJECTED')

class ReservationAdmin(admin.ModelAdmin):
    # Added 'purpose' to list_display
    list_display = ('lab', 'user', 'date', 'start_time', 'end_time', 'purpose', 'status')
    list_filter = ('status', 'date', 'lab')
    actions = [approve_reservations, reject_reservations]

admin.site.register(Reservation, ReservationAdmin)