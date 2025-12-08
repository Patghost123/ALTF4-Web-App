import os
import django

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CORE.settings')
django.setup()

# 2. Import your models
# We import from the apps where data exists
from labs.models import Lab, Equipment
from reservations.models import Reservation
# from notifications.models import Notification # Uncomment if you add models later
# from analytics.models import Analytics # Uncomment if you add models later

def clear_database():
    print("🧹 Starting database cleanup...")

    # 3. Delete Data (Order matters due to Foreign Keys!)
    
    # Delete Reservations first (because they depend on Labs and Users)
    deleted_count, _ = Reservation.objects.all().delete()
    print(f"   - Deleted {deleted_count} Reservations")


    print("\n✨ App data cleared! Users and Superusers are still safe.")

if __name__ == '__main__':
    # Add a simple confirmation prompt
    confirm = input("Are you sure you want to delete all Reservations? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("Operation cancelled.")