"""
URL configuration for CORE project.
"""
from django.contrib import admin
from django.urls import path, include
# We don't need 'from django import views' here, it causes confusion.
from . import views as root_views 

urlpatterns = [
    # NOTE: The root path ('') for the users app will point to /users/
    path('', root_views.home_redirect_view, name='home'),
    path('admin/', admin.site.urls),
    path('reservations/', include('reservations.urls')),
    path('labs/', include('labs.urls')), 
    path('profile/', root_views.profile, name='profile'),
    # REMOVED: path('auth/', root_views.interactive_auth, name='interactive_auth'), 
    # This URL is now defined directly in CORE/urls.py to match the LOGIN_URL=/auth/ setting.
]

from django.conf import settings
from django.conf.urls.static import static

# ... your existing urlpatterns ...

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)