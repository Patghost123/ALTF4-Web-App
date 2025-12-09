from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Lab
from .forms import LabForm, EquipmentFormSet # Import forms and formsets

# --- STANDARD VIEWS ---

@login_required
def index(request):
    """ Shows the map/list view of all labs """
    # Fetch ALL labs, regardless of is_active status
    labs = Lab.objects.all() 
    return render(request, 'labs/Labs_map.html', {'labs': labs})

@login_required
def lab_detail(request, slug):
    """ Detailed view for a specific lab """
    lab = get_object_or_404(Lab, slug=slug) 
    return render(request, 'labs/lab.html', {'lab': lab})

# --- NEW EDITING VIEW (Replaces LabUpdateView) ---

@staff_member_required
def lab_edit(request, slug):
    """
    Handles the editing of Lab details (LabForm) and its related Equipment (Formset).
    """
    lab = get_object_or_404(Lab, slug=slug)
    
    if request.method == 'POST':
        # 1. Handle main Lab details
        form = LabForm(request.POST, instance=lab)
        # 2. Handle related Equipment details
        formset = EquipmentFormSet(request.POST, request.FILES, instance=lab)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('labs:detail', slug=lab.slug)
        else:
            # If invalid, re-render form with errors (useful for debugging)
            print("Form or Formset validation failed:", form.errors, formset.errors)
    else:
        # Initial GET request
        form = LabForm(instance=lab)
        formset = EquipmentFormSet(instance=lab)
    
    # Render the combined form/formset template
    return render(request, 'labs/lab_form.html', {
        'lab': lab,
        'form': form,
        'formset': formset,
    })

def home_dashboard(request):
    available_labs = Lab.objects.filter(is_active=True) 
    return render(request, 'base.html', {
        'labs': available_labs
    })