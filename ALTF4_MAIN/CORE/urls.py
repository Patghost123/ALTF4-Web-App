"""
URL configuration for CORE project.
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views # Import views from the users app
from . import views as root_views 

urlpatterns = [
    # General app URLs
    path('', root_views.home_redirect_view, name='home'),
    path('admin/', admin.site.urls),
    path('reservations/', include('reservations.urls')),
    path('labs/', include('labs.urls')),
    path('analytics/', include('analytics.urls')), 
    path('users/', include('users.urls')),

    # Authentication Routes
    path('auth/', user_views.interactive_auth, name='interactive_auth'),
    path('logout/', user_views.logout_view, name='logout'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)