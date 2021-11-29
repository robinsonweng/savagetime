import os
from django.http import HttpResponse
from django.shortcuts import render
from .models import Video
from .models import Series


def index(request):
    series = Series.objects.all()
    videos = [s.video_set.order_by('-update_time')[0] for s in series]
    context = {
        'series': series,
        'videos': videos,
    }
    # add table update time
    return render(request, 'home/index.html', context)

def series(request, series_id):
    context = {}
    return render(request, 'home/view_series.html', context)

def video(request, video_id=0):
    # TODO: prevent django accessing file while uploading it
    # becareful about file access blockage
    # for test purpose
    video = Video.objects.order_by('-update_time')[0]
    video = os.path.join(video.file_field.url, "manifest.mpd")
    context = {'video_url': video}
    return render(request, 'home/view_video.html',context)

def search(request):
    keyword = request.GET.get('s')
    return HttpResponse(f"you search for {keyword}")

def error(request, query):
    return HttpResponse("404 yee")