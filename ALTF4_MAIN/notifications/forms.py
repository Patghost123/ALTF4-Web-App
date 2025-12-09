from django import forms

class AnnouncementForm(forms.Form):
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('staff', 'Staff Only'),
    ]

    TYPE_CHOICES = [
        ('info', 'Information (Blue)'),
        ('warning', 'Warning/Alert (Yellow)'),
        ('success', 'Success (Green)'),
    ]

    audience = forms.ChoiceField(choices=AUDIENCE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    notification_type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Enter announcement details...'}))