from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include



from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', include('accounts.urls')),
    path('', include('content.urls')),
    path('', include('pages.urls')),
    path('404/', lambda request: render(request, '404.html'), name='404'),
    path('about/', lambda request: render(request, 'about.html'), name='about'),
    path('portfolio/', lambda request: render(request, 'portfolio.html'), name='portfolio'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)