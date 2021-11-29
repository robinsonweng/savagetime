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

def video(request, series_id):
    # TODO: prevent nginx accessing same file while uploading it
    # becareful about file access blockage
    # for valadate approach purpose
    episode = request.GET['e']
    try:
        series = Series.objects.get(uuid=series_id)
        video = series.video_set.get(episode=episode)
    except ObjectDoesNotExist:
        raise Http404("Video id not found")

    context = {
        'video_set': series.video_set.order_by('episode'),
        'video': video,
    }
    return render(request, 'home/view_video.html',context)

def search(request):
    keyword = request.GET.get('s')
    return HttpResponse(f"you search for {keyword}")

def error(request, query):
    return HttpResponse("404 yee")