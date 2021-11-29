from django.db import models
from django.utils import timezone
import uuid # TODO: use admin user id for salt
from datetime import datetime


class Series(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(blank=True) # TODO: force uppercase before commit to db
    season = models.CharField(max_length=20, choices=[('春', '春'), ('夏', '夏'), ('秋', '秋'), ('冬', '冬')])
    episodes = models.IntegerField(blank=True)
    pub_year = models.CharField(max_length=20, choices=[(str(i), str(i)) for i in range(2000, datetime.today().year + 1)])
    pub_month = models.CharField(max_length=20, choices=[(str(i), str(i)) for i in range(1, 13)])
    finale = models.BooleanField(default=False)
    subtitle_group = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Video(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    series = models.ForeignKey('Series', on_delete=models.CASCADE, related_name='video_set')
    episode = models.CharField(max_length=20, null=True)
    update_time = models.DateTimeField(default=timezone.now)
    
    def filedir_path(instance, filename) -> str:
        """
        TODO: split episode into multiple folder for long series like Naruto
        Situation:
            Most anime are 12, 13, 25, 26 episodes as a set of series, aka season series. 
            The rest or it like HunterXHunter(new ver.)have total 148 episode,
            Fate/stay Night[Heaven's Feel] have 3 episode but 2h each. These two extrems
            may cause imbalance tree in linux FS(verificaiton required)
        """
        # only avalible for admin
        exet = filename.split('.')[1]
        return "{0}/{1}.{2}".format(instance.series_id, instance.uuid, exet)
    # filefield is not path!
    file_field = models.FileField(upload_to=filedir_path) # TODO:  should be array

    def __str__(self) -> str:
        return f"{self.series.name}[{self.episode}]"
