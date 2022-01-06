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


"""
    video/{video_id}/upload section
"""


@video_router.api_operation(["POST"], "/upload", response=NOT_SET, url_name="post_upload_video")
def create_video_metadata(request, metadata: Videoin):
    """
        create a session for uploading
    """
    length_header = "X-upload-content-length"
    type_header = "X-upload-content-type"
    upload_content_length = request.headers.get(length_header)
    upload_content_type = request.headers.get(type_header)

    series = Series.objects.filter(name=metadata.series_name)
    if not series.exists():
        return {"status": "Series name not found"}
    if Video.objects.filter(episode=metadata.episode).exists():
        return {"status": "Video already exist"}

    upload_id = None
    while (upload_id is None) or (upload_id in request.session):  # may cause problem
        salt = os.urandom(5)  # generate salt for upload id
        upload_id = base64.b64encode(salt).decode()

    # init session
    session_data = {  # metadata
        "x_length": upload_content_length,
        "x_type": upload_content_type,
        "series_name": metadata.series_name,
        "episode": metadata.episode,
        "file_name": metadata.file_name,
        "series_id": str(series[0].uuid),
    }
    # using session may violate restful principle, use cache instead
    request.session[upload_id] = session_data

    return {
        "status": "200",
        "upload_url": f"{reverse('api-dev:put_video')}?upload_id={upload_id}"
    }


@video_router.api_operation(
    ["PATCH"],
    "/upload",
    response={no_response_body_set: None},
    url_name=""
)
def upload_video(request, upload_id: str):
    """
        This route do two things:
            1. start a upload session
            2. check the status of an upload
            3. resume the upload
    """
    # check session
    upload_session = (request.session.get(upload_id, None) is not None)
    if not upload_session:
        raise InvalidQuery(400, "id not found or session expire")

    # 1. do request header check
    # 2. identify the user demand
    # 3.

    chunk = FileChunk.load_chunk(request)
    case = chunk.get_case()
    if case == "status":
        progress = Uploader.get_progress(upload_id)
        if progress is None:
            return UnexpetedRequest(400, "no progress to report")
        # return status head
        headers = {
            'Range': f"{progress}"
        }
        return UploadStatusResponse(headers, status=308)
        # ^ this kind of response should put at upload controller
    elif case == "error":
        return InvalidHeader(400)

    # start upload
    if case == "resume":
        uploader = Uploader.resume_upload(chunk)
    elif case == "new":
        uploader = Uploader.init_upload(chunk)
    uploader.receve_upload(chunk)

    if not uploader.is_complete():  # 204
        headers = {

        }
        return UploadStatusResponse(headers, 204)
    # return metadata for db

    # flush everything in cache
    uploader.flush(option="cache")
    headers = {

    }
    return UploadStatusResponse(headers, 201)


@video_router.api_operation(["DELETE"], "/upload", response=NOT_SET, url_name="")
def clear_upload_session(request, upload_id: str):
    pass


"""
    video/{video_id}/info section
"""


@video_router.api_operation(["GET"], "{video_id}/info", response=NOT_SET, url_name="")
def get_video_info(request, video_id: str):
    pass


@video_router.api_operation(["POST"], "{video_id}/info", response=NOT_SET, url_name="")
def post_video_info(request, video_id: str):
    pass


@video_router.api_operation(["PATCH"], "{video_id}/info", response=NOT_SET, url_name="")
def patch_video_info(request, video_id: str):
    pass


@video_router.api_operation(["DELETE"], "{video_id}/info", response=NOT_SET, url_name="")
def delete_video_info(request, video_id: str, delete_file: bool):
    pass


"""
    video/{video_id}/series section
"""


@video_router.api_operation(["GET"], "{video_id}/series")
def get_video_series(request, video_id: str):
    pass
