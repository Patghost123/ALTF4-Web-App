from django.db import models
from django.contrib.auth.models import User
from labs.models import Lab, Equipment

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE) 
    # New field for equipment selection
    equipment = models.ManyToManyField(Equipment, blank=True, related_name='reservations')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.TextField(help_text="Reason for booking (e.g., Thesis Research, Class Project)")
    
    # New field for admin feedback
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason why the admin rejected this request")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lab.name} - {self.date} ({self.start_time}-{self.end_time}) [{self.status}]"