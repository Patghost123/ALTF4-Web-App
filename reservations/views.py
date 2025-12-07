from django.shortcuts import render, redirect
from .forms import ReservationForm
from .models import Reservation

def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('reservation_success')
    else:
        form = ReservationForm()
    return render(request, 'reservations/reserve.html', {'form': form})

def reservation_success(request):
    return render(request, 'reservations/success.html')
