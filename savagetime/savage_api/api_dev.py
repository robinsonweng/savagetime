import os
import base64
from django.http import (Http404)
from django.shortcuts import (get_object_or_404)
from django.core.cache import caches  # using the default cache
from django.contrib.auth import (authenticate)
from ninja import (NinjaAPI)
from savage_api.schemas import (
    UserLogin, PureText, Videoget, Videoin
)
from savage_api.models import (Video, Series)
from savage_api.uploader import (
    FileChunk, UploaderFile
)
from savage_api.exceptions import (
    InvalidHeader, InvalidQuery, UnexpetedRequest
)


api = NinjaAPI(version='0.1.0')


@api.get("/video")
def get_video_url():
    pass


@api.post("/video")
def post_upload_metadata():
    """
    c: upload the metadata
    s: response an url for upload
    if interrupt then use head & patch (tus)
    """
    pass


@api.put("/video")
def modify_video():
    pass


@api.delete("/video")
def delete_video():
    pass


@api.get("/search")
def keyword_search():
    """
    text search in db
    """
    pass


@api.get("/authorize")
def get_user_athorize():
    """
    return user authorize status
    """
    pass


@api.post("/authorize")
def post_user_athorize():
    """
    route for user authorizing
    """
