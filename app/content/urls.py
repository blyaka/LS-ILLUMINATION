from django.urls import path
from .views import video_test

urlpatterns = [
    path('video-test/<uuid:pk>/', video_test, name='video_test'),
]