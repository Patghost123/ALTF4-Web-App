from django import forms
from django.contrib.auth.models import User
from .models import Profile

# Form to edit basic user info (username, email)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

# Form to edit profile info (image, course, year, interest)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'course', 'year_of_study', 'area_of_interest']