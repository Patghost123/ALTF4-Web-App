"""
URL configuration for CORE project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views as root_views 

urlpatterns = [
    path('', root_views.home_redirect_view, name='home'),
    path('admin/', admin.site.urls),
    path('reservations/', include('reservations.urls')),
    path('labs/', include('labs.urls')),
    
    # NEW: Include the analytics app
    path('analytics/', include('analytics.urls')), 
    path('users/', include('users.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)