from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # New Admin Route
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # New User Route
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    
    path('reserve/<int:lab_id>/', views.make_reservation, name='make_reservation'),
    path('success/', views.reservation_success, name='success'),
    path('timetable/', views.timetable, name='timetable'),
    path('api/events/', views.all_reservations_api, name='all_reservations_api'),
]