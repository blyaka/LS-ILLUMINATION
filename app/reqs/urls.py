from django.urls import path
from .views import submit_request

urlpatterns = [
    path('submit/', submit_request, name='req_submit'),
]
