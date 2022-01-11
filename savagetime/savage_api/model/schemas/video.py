from ninja import (Schema, ModelSchema)
from ..models import (Video)


class UserLogin(Schema):
    username: str
    passwd: str


class VideoInfo(Schema):
    uuid: str
    series_name: str
    episode: str
    update_time: str


class VideoInfoPostInput(Schema):
    episode: str
    file_name: str


class VideoInfoPatchInput(Schema):
    episode: str = None
    file_name: str = None


class VideoUploadPostInput(Schema):
    series_name: str
    episode: str
    file_name: str


class Videoget(ModelSchema):
    class Config:
        model = Video
        model_fields = [
            "episode"
        ]


class PureText(Schema):
    status: str
