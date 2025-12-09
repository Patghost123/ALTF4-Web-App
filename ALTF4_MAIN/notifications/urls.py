from django.urls import path
from . import views

app_name = 'notifications'
urlpatterns = [
    path('mark_read/<int:notif_id>/', views.mark_read, name='mark_read'),
    path('announce/', views.create_announcement, name='create_announcement'),
]