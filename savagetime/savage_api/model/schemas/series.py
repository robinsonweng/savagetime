from ninja import Schema, ModelSchema

from ..models import Video, Series

from django.utils import timezone


class SeriesInputBase(Schema):
    def __setattr__(self, name, value):
        if name == "season":
            season_zhtw = ["春", "夏", "秋", "冬"]
            if value not in season_zhtw:
                raise AttributeError(f"value: '{value}' is not a member of {season_zhtw}")
        elif name == "pub_year":
            current_year = timezone.now().year
            year = [y for y in range(1999, current_year + 1)]
            if value not in year:
                raise AttributeError(f"value: '{value}' is not a member of {year}")
        elif name == "pub_month":
            month = [m for m in range(1, 12 + 1)]
            if value not in month:
                raise AttributeError(f"value: '{value}' is not a member of {month}")
        return super().__setattr__(name, value)


class SeriesInfoOutput(Schema):
    uuid: str
    season: str
    episodes: int
    pub_year: str
    pub_month: str
    finale: bool
    subtitle_group: str = None


class SeriesInfoPostInput(SeriesInputBase):
    name: str
    season: str
    episodes: int
    pub_year: str
    pub_month: str
    finale: bool
    subtitle_group: str = None


class SeriesInfoPatchInput(SeriesInputBase):
    name: str = None
    season: str = None
    episodes: int = None
    pub_year: str = None
    pub_month: str = None
    finale: bool = None
    subtitle_group: str = None
