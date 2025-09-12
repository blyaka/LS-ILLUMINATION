from django.shortcuts import render
from content.models import Video
from django.utils import timezone


def HomePage(request):
    hero = Video.objects.filter(status='ready', is_featured=True).first()
    more = Video.objects.filter(status='ready', is_featured=False).order_by('-created')
    return render(request, 'home.html', {'hero_video': hero, 'more_videos': more})


def AboutPage(request):
    ctx = {
        "today": timezone.now(),
    }

    return render(request, 'about.html', ctx)

def PortfolioPage(request):
    ctx = {
        "today": timezone.now(),
    }

    return render(request, 'portfolio.html', ctx)



def Custom404(request, exception):
            return render(request, '404.html', status=404)