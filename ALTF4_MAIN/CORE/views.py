from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from labs.models import Lab

# Protect the home view so users cannot bypass login to see the dashboard
@login_required
def home_redirect_view(request):
    # 2. FETCH THE DATA
    # We filter by is_active=True so only active labs show on the dashboard
    labs = Lab.objects.filter(is_active=True) 
    
    # 3. PASS THE DATA TO THE TEMPLATE
    context = {
        'labs': labs
    }
    
    return render(request, 'base.html', context)