from django.urls import path
from . import views

# Add the app_name to support namespace lookups (e.g., 'reservations:timetable')
app_name = 'reservations'

urlpatterns = [
    path('reserve/', views.make_reservation, name='make_reservation'),
    path('success/', views.reservation_success, name='success'),
    path('timetable/', views.timetable, name='timetable'),
]