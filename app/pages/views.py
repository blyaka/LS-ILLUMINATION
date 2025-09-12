from django.shortcuts import render, get_object_or_404
from content.models import Video
from cases.models import Category, Case
from django.utils import timezone


def HomePage(request):
    categories = Category.objects.all().order_by("order")
    for cat in categories:
        words = cat.name.split()
        cat.first_word = words[0]
        cat.rest_words = " ".join(words[1:]) if len(words) > 1 else ""

    hero = Video.objects.filter(status='ready', is_featured=True).first()
    more = Video.objects.filter(status='ready', is_featured=False).order_by('-created')

    ctx = {'hero_video': hero,
           'more_videos': more,
           'categories': categories,
        }

    return render(request, 'home.html', ctx)


def AboutPage(request):
    ctx = {
        "today": timezone.now(),
    }

    return render(request, 'about.html', ctx)

def PortfolioPage(request, slug):
    category = get_object_or_404(Category, slug=slug)
    cases = category.cases.all().order_by("order")

    ctx = {
        "today": timezone.now(),
        'category': category,
        'cases': cases,
    }

    return render(request, 'portfolio.html', ctx)



def Custom404(request, exception):
            return render(request, '404.html', status=404)