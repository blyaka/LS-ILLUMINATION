from django.urls import path
from .views import HomePage, AboutPage

urlpatterns = [
    path('', HomePage, name='home'),
    path('about/', AboutPage, name='about'),
]