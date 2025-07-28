"""
URL configuration for legaldoc_ai project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # User authentication URLs
    path('', include('user_auth.urls')),
    # API URLs
    path('api/', include('document_analyzer.urls', namespace='document_analyzer_api')),
    # Main app URLs
    path('', RedirectView.as_view(url='document_analyzer/', permanent=True)),
    path('document_analyzer/', include('document_analyzer.urls', namespace='document_analyzer')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
