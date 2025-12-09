from .models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        # Get unread notifications
        notifs = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'notifications_list': notifs,
            'unread_count': notifs.count()
        }
    return {}