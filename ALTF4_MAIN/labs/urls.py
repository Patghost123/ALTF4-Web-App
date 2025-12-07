from django.urls import path
from . import views

app_name = 'labs'
urlpatterns = [
    path('', views.index, name='index'), 
    path('<slug:slug>/edit/', views.LabUpdateView.as_view(), name='edit'), 
    path('<slug:slug>/', views.lab_detail, name='detail'),
]