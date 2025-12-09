from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from .models import Notification
from .forms import AnnouncementForm

@login_required
def mark_read(request, notif_id):
    notif = Notification.objects.get(id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', '/')) # Reloads the same page

User = get_user_model()

@staff_member_required
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            audience = form.cleaned_data['audience']
            msg = form.cleaned_data['message']
            notif_type = form.cleaned_data['notification_type']

            # 1. Filter Recipients
            if audience == 'students':
                recipients = User.objects.filter(is_staff=False, is_superuser=False)
            elif audience == 'staff':
                recipients = User.objects.filter(is_staff=True)
            else:
                recipients = User.objects.all()

            # 2. Bulk Create Notifications
            notifications_to_create = []
            for user in recipients:
                notifications_to_create.append(
                    Notification(
                        recipient=user,
                        message=msg,
                        notification_type=notif_type,
                        category='announcement' # THIS IS THE KEY CHANGE
                    )
                )
            
            Notification.objects.bulk_create(notifications_to_create)
            
            messages.success(request, f"Announcement sent to {len(notifications_to_create)} users.")
            return redirect('notifications:create_announcement') # Redirect to same page or dashboard
    else:
        form = AnnouncementForm()

    return render(request, 'notification/send_announcement.html', {'form': form})

