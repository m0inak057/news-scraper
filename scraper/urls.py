from django.urls import path
from . import views

urlpatterns = [
    path('', views.scrape_headlines, name='scrape_headlines'),
]
