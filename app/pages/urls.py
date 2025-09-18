from django.urls import path
from .views import HomePage, AboutPage, PortfolioPage, TestPage

urlpatterns = [
    path('', HomePage, name='home'),
    path('about/', AboutPage, name='about'),
    path('portfolio/<slug:slug>/', PortfolioPage, name='portfolio'),
    path('test/', TestPage, name='test'),

]