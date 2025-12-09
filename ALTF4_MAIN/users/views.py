from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages



from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages

# Your existing view (keeps rendering base.html)
def home_redirect_view(request):
    return render(request, 'base.html')

# The NEW Advanced Auth View
def interactive_auth(request):
    # Initialize forms for GET requests
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()

    if request.method == 'POST':
        # LOGIC: Check which button was pressed ('submit_login' or 'submit_signup')
        
        # --- Handle Login ---
        if 'submit_login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                # Redirect to your home page after successful login
                return redirect('home') 
            else:
                messages.error(request, "Invalid username or password.")

        # --- Handle Signup ---
        elif 'submit_signup' in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                # Redirect to home after successful signup
                return redirect('home')
            else:
                # This catches weak passwords or existing usernames
                messages.error(request, "Signup failed. Check password requirements.")

    context = {
        'login_form': login_form,
        'signup_form': signup_form
    }
    
    # Make sure your HTML file from the previous step is named 'auth.html'
    return render(request, 'account/auth.html', context)

from django.contrib.auth.decorators import login_required

# ... your existing imports ...

@login_required # Forces user to be logged in to see this
def profile(request):
    return render(request, 'account/profile.html')