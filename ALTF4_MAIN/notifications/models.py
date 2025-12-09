from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
    )
    
    # NEW: Add Categories
    CATEGORIES = (
        ('reservation', 'Reservation Update'),
        ('announcement', 'Public Announcement'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='info')
    
    # NEW: The field to filter by
    category = models.CharField(max_length=20, choices=CATEGORIES, default='reservation')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.upper()}: {self.message}"