from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import Lab
from .forms import LabForm

def index(request):
    """ Shows the map/list view of all labs """
    labs = Lab.objects.filter(is_active=True)
    return render(request, 'labs/Labs_map.html', {'labs': labs})

def lab_detail(request, slug):
    """ Detailed view for a specific lab """
    lab = get_object_or_404(Lab, slug=slug) 
    return render(request, 'labs/lab.html', {'lab': lab})

@method_decorator(staff_member_required, name='dispatch')
class LabUpdateView(UpdateView):
    """
    Allows staff members (admins) to edit existing Lab details.
    
    Uses LabForm for automatic handling of field validation and saving.
    Requires staff_member_required decorator for security.
    """
    model = Lab
    form_class = LabForm
    template_name = 'labs/Lab_form.html'
    
    # After successful update, redirect back to the lab detail page
    def get_success_url(self):
        # We use the slug of the updated object (self.object) for the redirect
        return reverse_lazy('labs:detail', kwargs={'slug': self.object.slug})