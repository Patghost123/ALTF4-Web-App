from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Protect the home view so users cannot bypass login to see the dashboard
@login_required
def home_redirect_view(request):
    return render(request, 'base.html')