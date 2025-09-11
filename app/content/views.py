from django.shortcuts import get_object_or_404, render
from .models import Video

def video_test(request, pk):
    v = get_object_or_404(Video, pk=pk)
    return render(request, 'content/video_test.html', {'video': v})