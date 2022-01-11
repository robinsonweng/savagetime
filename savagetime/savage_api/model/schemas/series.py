from ninja import Schema, ModelSchema

from ..models import Video, Series

from django.utils import timezone




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
