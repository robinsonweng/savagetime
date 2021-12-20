from django.db import models

# Create your models here.

from django.utils import timezone
import uuid  # TODO: What if uuid repeat?


class Series(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(blank=True)
    season = models.CharField(max_length=20)
    episodes = models.IntegerField(blank=True)
    pub_year = models.CharField(max_length=20)
    pub_month = models.CharField(max_length=20)
    finale = models.BooleanField(default=False)
    subtitle_group = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Video(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        update:
            these two extremes will cause imbalance directory tree and
            Inode table search inefficient in linx FS, but the solution is not long-term.
            It would be a better idea to mount spacific linux FS for large file storage
        """
        exet = filename.split('.')[1]
        return "{0}/{1}.{2}".format(instance.series_id, instance.uuid, exet)
    file_field = models.FileField(upload_to=filedir_path)

    def __str__(self) -> str:
        return f"{self.series.name}[{self.episode}]"
