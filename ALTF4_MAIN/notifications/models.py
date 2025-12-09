from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPES = (
        ('info', 'Info'),       # For announcements
        ('success', 'Success'), # For accepted reservations
        ('warning', 'Warning'), # For pending/rejected
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message}"