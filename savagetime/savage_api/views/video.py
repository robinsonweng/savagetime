# view functions for video route

import os
import uuid
import base64

from django.urls import reverse

from django.http import HttpResponseBadRequest
from django.core.exceptions import (
    ObjectDoesNotExist, ValidationError
)

from ..libs.route import SavageRouter
from ninja.constants import NOT_SET

from ..model.models import (
    Video, Series
)
from ..model.schemas.video import (
    VideoUploadPostInput, VideoInfo, VideoInfoPostInput, VideoInfoPatchInput
)
# custom exceptions
from ..responses.exceptions import (
    InvalidQuery, InvalidHeader, UnexpetedRequest
)
from ..responses.response import (
    UploadStatusResponse, NoBodyResponse
)

from ..utils.uploader import Uploader, FileChunk


no_response_body_set = frozenset({201, 204, 308})

video_router = SavageRouter()
video_router.prefix = "video/"  # set the root route


"""
    video/{video_id}/stream section
"""


@video_router.api_operation(
    ["GET"],
    "/{video_id}/stream",
    response=NOT_SET,
    url_name="video_stream"
)
def get_video_stream(request, video_id: str):
    pass


"""
    video/{video_id}/upload section
"""


@video_router.api_operation(["POST"], "/upload", response=NOT_SET, url_name="video_upload")
def create_video_metadata(request, metadata: VideoUploadPostInput):
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
        "upload_url": f"{reverse('api-dev:post_upload_video')}?upload_id={upload_id}"
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
    upload_session = request.session.get(upload_id, None)
    if upload_session is None:
        raise InvalidQuery(400, f"id: {upload_id} not found or session expire")

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
        uploader = Uploader.init_upload(upload_id, upload_session["metadata"], chunk)
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


@video_router.api_operation(["GET"], "{video_id}/info", response=VideoInfo, url_name="", auth=None)
def get_video_info(request, video_id: str):
    # video_id = "0b206681-573a-42bc-b38b-52689bb8f5ea"
    video_id = "123"
    try:
        video = Video.objects.get(uuid=video_id)
    except ObjectDoesNotExist:
        raise InvalidQuery(404, f"Id not found: {video_id}")
    except ValidationError:
        return HttpResponseBadRequest(None, 400)
    return video


@video_router.api_operation(["POST"], "/info", response=VideoInfo, url_name="")
def post_video_info(
    request,
    data: VideoInfoPostInput,
    series_id: str = None,
    series_name: str = None
):
    # try/catch
    if (series_id is not None) and (series_name is None):
        try:
            series = Series.objects.get(uuid=series_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(None, 404)
        except ValidationError:
            return HttpResponseBadRequest(None, 400)
    elif (series_id is None) and (series_name is not None):
        try:
            series = Series.objects.get(name=series_name)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(None, 404)
        except ValidationError:
            return HttpResponseBadRequest(None, 400)
    else:
        return HttpResponseBadRequest(None, 400)
    return {"123": "123"}


@video_router.api_operation(["PATCH"], "{video_id}/info", response=NOT_SET, url_name="")
def patch_video_info(
    request,
    video_id: str,
    data: VideoInfoPatchInput,
    series_id: str = None,
    series_name: str = None
):
    try:
        video = Video.objects.get(uuid=video_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(None, 404)
    except ValidationError:
        return HttpResponseBadRequest(None, 400)

    post_field = [f for f in VideoInfoPostInput.__dict__["__fields__"]]
    # check field that is not none
    for f in post_field:
        attr = getattr(data, f)
        if attr is not None:
            setattr(video, f, attr)
    try:
        video.save()
    except Exception as e:
        print(e)
        return HttpResponseBadRequest(None, 400)
    return NoBodyResponse(201)  # created


@video_router.api_operation(["DELETE"], "{video_id}/info", response=NOT_SET, url_name="")
def delete_video_info(request, video_id: str):
    try:
        video = Video.objects.get(uuid=video_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(None, 404)
    except ValidationError:
        return HttpResponseBadRequest(None, 400)
    try:
        video.delete()
    except Exception as e:
        print(e)
        return HttpResponseBadRequest(None, 400)
    return NoBodyResponse(201)


"""
    video/{video_id}/series section
"""


@video_router.api_operation(["GET"], "{video_id}/series", auth=None)
def get_series_from_video(request, video_id: str):
    pass
