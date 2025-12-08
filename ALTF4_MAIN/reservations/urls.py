from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('reserve/<int:lab_id>/', views.make_reservation, name='make_reservation'),
    path('success/', views.reservation_success, name='success'),
    path('timetable/', views.timetable, name='timetable'),
    # New API path for the calendar
    path('api/events/', views.all_reservations_api, name='all_reservations_api'),
]