from django.shortcuts import render, get_object_or_404
from content.models import Video, News
from cases.models import Category, Case, Subcategory
from django.utils import timezone
from django.db.models import Prefetch


def HomePage(request):
    categories = Category.objects.all().order_by("order")
    for cat in categories:
        words = cat.name.split()
        cat.first_word = words[0]
        cat.rest_words = " ".join(words[1:]) if len(words) > 1 else ""

    hero = Video.objects.filter(status='ready', placement='hero').first()
    gallery = Video.objects.filter(status='ready', placement='gallery').order_by('position','-created')
    blocks = Video.objects.filter(status='ready', placement='block').order_by('position','-created')

    news = News.objects.filter(is_available=True).order_by('-created_at')

    ctx = {
        'hero_video': hero,
        'more_videos': gallery,
        'block_videos': blocks,
        'categories': categories,
        'news': news,
    }
    return render(request, 'home.html', ctx)


def AboutPage(request):
    ctx = {
        "today": timezone.now(),
    }

    return render(request, 'about.html', ctx)



def PortfolioPage(request, slug):
    category = get_object_or_404(
        Category.objects.prefetch_related(
            Prefetch('subcategories', queryset=Subcategory.objects.order_by('order')),
            Prefetch('cases', queryset=Case.objects.filter(subcategory__isnull=True).order_by('order')),
        ),
        slug=slug
    )

    subcategories = list(category.subcategories.all())

    cases_sub_qs = (
        Case.objects.filter(subcategory__category=category)
        .select_related('subcategory')
        .order_by('subcategory__order', 'order')
    )
    cases_by_sub = {}
    for c in cases_sub_qs:
        cases_by_sub.setdefault(c.subcategory, []).append(c)

    direct_cases = list(category.cases.all())

    use_grouped = bool(subcategories) or bool(cases_by_sub)

    ctx = {
        "today": timezone.now(),
        "category": category,
        "subcategories": subcategories,
        "cases_by_sub": cases_by_sub,
        "direct_cases": direct_cases,
        "use_grouped": use_grouped,
    }
    return render(request, 'portfolio.html', ctx)




def Custom404(request, exception):
            return render(request, '404.html', status=404)