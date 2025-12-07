from django.shortcuts import render, get_object_or_404
from .models import Lab

def index(request):
    """ Shows the map/list view of all labs """
    labs = Lab.objects.filter(is_active=True)
    return render(request, 'labs/index.html', {'labs': labs})

def lab_detail(request, slug):
    lab = get_object_or_404(Lab, slug=slug) 
    return render(request, 'labs/detail.html', {'lab': lab})