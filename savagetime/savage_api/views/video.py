# view functions for video route

import os
import base64

from django.urls import reverse

from ninja import Router
from ninja.constants import NOT_SET

from ..model.models import (
    Video, Series
)
from ..model.schemas import (
    Videoget, Videoin
)

from ..responses.exceptions import (
    InvalidQuery, InvalidHeader, UnexpetedRequest
)
from ..responses.response import (
    UploadStatusResponse
)

from ..utils.uploader import Uploader, FileChunk


no_response_body_set = frozenset({201, 204, 308})

video_router = Router()
video_router.prefix = "video/"  # set the root route


"""
    video/{video_id}/stream section
"""


@video_router.api_operation(["GET"], "/{video_id}/stream", response=NOT_SET, url_name="")
def get_video_stream(request, video_id: str):
    pass


