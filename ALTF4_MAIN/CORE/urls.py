"""
URL configuration for CORE project.
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views 
from . import views as root_views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home
    path('', root_views.home_redirect_view, name='home'), 
    
    # Admin
    path('admin/', admin.site.urls),

    # App URLs
    path('reservations/', include('reservations.urls')),
    path('labs/', include('labs.urls')),
    path('analytics/', include('analytics.urls')), 
    path('users/', include('users.urls')),
    
    # Notifications
    path('notifications/', include('notifications.urls')),

    # Authentication
    path('auth/', user_views.interactive_auth, name='interactive_auth'),
    path('logout/', user_views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)