from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
# Change 'reservations.models' to match your actual app/model name
from reservations.models import Reservation 
from .models import Notification

User = get_user_model()

@receiver(post_save, sender=Reservation)
def reservation_notification(sender, instance, created, **kwargs):
    """
    Triggered when a Reservation is saved.
    """
    # 1. New Reservation Created -> Notify Admin/Staff
    if created:
        staff_users = User.objects.filter(is_staff=True)
        for staff in staff_users:
            Notification.objects.create(
                recipient=staff,
                # FIX: Change instance.student to instance.user
                message=f"New reservation pending from {instance.user.first_name} for {instance.lab.name}.",
                notification_type='warning'
            )

    # 2. Status Updated -> Notify Student/User
    else:
        # Check the status
        if instance.status == 'CONFIRMED': # Ensure this matches your model choices (CONFIRMED vs APPROVED)
            Notification.objects.create(
                # FIX: Change instance.student to instance.user
                recipient=instance.user, 
                message=f"Good news! Your reservation for {instance.lab.name} has been CONFIRMED.",
                notification_type='success'
            )
        elif instance.status == 'REJECTED':
             Notification.objects.create(
                # FIX: Change instance.student to instance.user
                recipient=instance.user,
                message=f"Update: Your reservation for {instance.lab.name} was DECLINED.",
                notification_type='warning'
            )