from ninja import (Schema, ModelSchema)
from savagetime.savage_api.model.models import (Video)


class UserLogin(Schema):
    username: str
    passwd: str


class Videoin(Schema):
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