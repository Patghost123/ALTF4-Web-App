from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
# Change 'reservations.models' to match your actual app/model name
from reservations.models import Reservation 
from .models import Notification

User = get_user_model()

@receiver(post_save, sender=Reservation)
def reservation_notification(sender, instance, created, **kwargs):
    if created:
        staff_users = User.objects.filter(is_staff=True)
        for staff in staff_users:
            Notification.objects.create(
                recipient=staff,
                message=f"New reservation pending from {instance.user.first_name} for {instance.lab.name}.",
                notification_type='warning',
                category='reservation' # Explicitly tag as reservation
            )

    else:
        if instance.status == 'CONFIRMED':
            Notification.objects.create(
                recipient=instance.user,
                message=f"Good news! Your reservation for {instance.lab.name} has been CONFIRMED.",
                notification_type='success',
                category='reservation' # Tag as reservation
            )
        elif instance.status == 'REJECTED':
             Notification.objects.create(
                recipient=instance.user,
                message=f"Update: Your reservation for {instance.lab.name} was DECLINED.",
                notification_type='warning',
                category='reservation' # Tag as reservation
            )