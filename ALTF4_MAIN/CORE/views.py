from django.shortcuts import render

def home_redirect_view(request):
    # Instead of redirecting, render base.html
    return render(request, 'base.html')