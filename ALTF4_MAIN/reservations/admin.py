from django.contrib import admin
from .models import Reservation, ReservationEquipment

class ReservationEquipmentInline(admin.TabularInline):
    model = ReservationEquipment
    extra = 1
    # Removed autocomplete_fields to prevent admin.E039 error.
    # This requires EquipmentAdmin (in labs/admin.py) to have search_fields defined.
    # autocomplete_fields = ['equipment']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab', 'user', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'lab')
    search_fields = ('user__username', 'lab__name', 'purpose')
    inlines = [ReservationEquipmentInline]
    
    # We must exclude 'equipment' from the main form because it has a 'through' model
    # and cannot be edited by the standard M2M widget.
    exclude = ('equipment',) 

# You can register the through model directly if you want to see all item allocations
@admin.register(ReservationEquipment)
class ReservationEquipmentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'equipment', 'quantity')