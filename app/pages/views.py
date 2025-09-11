from django.shortcuts import render
from content.models import Video


def HomePage(request):
    hero = Video.objects.filter(status='ready', is_featured=True).first()
    more = Video.objects.filter(status='ready', is_featured=False).order_by('-created')
    return render(request, 'home.html', {'hero_video': hero, 'more_videos': more})
