from django.db import models
from django.contrib.auth.models import User
from labs.models import Lab  # Import the Lab model

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Changed from 'room' (text) to 'lab' (link to Lab model)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE) 
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lab.name} - {self.date} ({self.start_time}-{self.end_time})"