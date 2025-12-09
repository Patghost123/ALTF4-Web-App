from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages

# Your existing view (keeps rendering base.html)
def home_redirect_view(request):
    return render(request, 'base.html')

