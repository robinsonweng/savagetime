from django.contrib import admin
from home import models
# Register your models here.

admin.site.register(models.Season)
admin.site.register(models.Series)
admin.site.register(models.Video)