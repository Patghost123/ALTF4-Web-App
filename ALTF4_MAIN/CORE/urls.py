"""
URL configuration for CORE project.
"""
from django.contrib import admin
from django.urls import path, include
from labs import views as lab_views
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views # Import views from the users app
from . import views as root_views 

urlpatterns = [
    # General app URLs
    path('', lab_views.home_dashboard, name='home'),
    path('admin/', admin.site.urls),
    path('reservations/', include('reservations.urls')),
    path('labs/', include('labs.urls')),
    path('analytics/', include('analytics.urls')), 
    path('users/', include('users.urls')),
    path('auth/', user_views.interactive_auth, name='interactive_auth'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)