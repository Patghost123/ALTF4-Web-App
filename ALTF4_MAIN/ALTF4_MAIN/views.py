from django.shortcuts import redirect

def home_redirect_view(request):
    return redirect('labs:index')