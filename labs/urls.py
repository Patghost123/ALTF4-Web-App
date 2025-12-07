from django.urls import path
from . import views

app_name = 'labs'
urlpatterns = [
    path('', views.index, name='index'), # Map view usually goes here
    path('<slug:slug>/', views.lab_detail, name='detail'),
]