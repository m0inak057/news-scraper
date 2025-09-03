"""
URL configuration for newscraper project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('scraper.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
