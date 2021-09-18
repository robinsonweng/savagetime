from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("this is our home")

def series(request, series_id):
    return HttpResponse("select series here")

def video(request, video_id=0):
    return HttpResponse("shows pecific video here")

def search(request, query):
    return HttpResponse("return search result")

def error(request, query):
    return HttpResponse("404 yee")