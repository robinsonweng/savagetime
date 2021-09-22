from django import template
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index(request):
    return HttpResponse("this is our home")

def series(request, series_id):
    temp = loader.get_template('view_series.html')
    context = {}
    return HttpResponse(temp.render(context, request))

def video(request, video_id=0):
    temp = loader.get_template('view_video.html')
    context = {}
    return HttpResponse(temp.render(context, request))

def search(request):
    keyword = request.GET.get('s')
    return HttpResponse(f"you search for {keyword}")

def error(request, query):
    return HttpResponse("404 yee")