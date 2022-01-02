from django.contrib import admin
from savage_api import models

# Register your models here.


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid',  'get_video_amount', 'episodes']
    # add search fields when adding video
    # TODO: add filter by date
    ordering = ['pk']
    search_fields = ['name']

    @admin.display(description="video current amount")
    def get_video_amount(self, obj) -> int:
        # get local episode from db
        return obj.video_set.count()


@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['get_series_name', 'uuid', 'episode']
    autocomplete_fields = ['series']

    @admin.display(description="Series name")
    def get_series_name(self, obj) -> str:
        # custom video page display
        return obj.series.name
