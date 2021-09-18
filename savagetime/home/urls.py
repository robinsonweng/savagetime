from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('series/<int:series_id>/', views.series, name='series'),
    path('video/<int:video_id>/', views.video, name='video'),
    path('search/<str:query>/', views.search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
