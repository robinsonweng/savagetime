import os
from django.http import HttpResponse
from django.shortcuts import render
from .models import Video
from .models import Series


def index(request):
    temp = loader.get_template('index.html')
    context = {}
    return HttpResponse(temp.render(context, request))

def series(request, series_id):
    temp = loader.get_template('view_series.html')
    context = {}
    return HttpResponse(temp.render(context, request))

def video(request, video_id=0):
    # TODO: prevent django accessing file while uploading it
    # becareful about file access blockage
    temp = loader.get_template('view_video.html')
    context = {}
    return HttpResponse(temp.render(context, request))

def search(request):
    keyword = request.GET.get('s')
    return HttpResponse(f"you search for {keyword}")

def error(request, query):
    return HttpResponse("404 yee")