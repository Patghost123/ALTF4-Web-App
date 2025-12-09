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
    
    # Updated to use a 'through' model to store quantity for each item
    equipment = models.ManyToManyField(
        Equipment, 
        blank=True, 
        related_name='reservations',
        through='ReservationEquipment'
    )
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.TextField(help_text="Reason for booking (e.g., Thesis Research, Class Project)")
    
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason why the admin rejected this request")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lab.name} - {self.date} ({self.start_time}-{self.end_time}) [{self.status}]"

class ReservationEquipment(models.Model):
    """
    Intermediate model to store how many of a specific equipment 
    are reserved in a single reservation.
    """
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('reservation', 'equipment')

    def __str__(self):
        return f"{self.quantity}x {self.equipment.name} for {self.reservation}"