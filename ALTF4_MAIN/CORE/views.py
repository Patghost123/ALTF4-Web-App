from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from labs.models import Lab
from notifications.models import Notification

@login_required
def home_redirect_view(request):
    labs = Lab.objects.filter(is_active=True) 
    
    recent_announcements = Notification.objects.filter(
        recipient=request.user,
        category='announcement' 
    ).order_by('-created_at')[:5]

    context = {
        'labs': labs,
        'recent_notifications': recent_announcements,
    }
    
    return render(request, 'base.html', context)