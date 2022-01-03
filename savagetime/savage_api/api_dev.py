import os
import base64
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import (authenticate)
from ninja import (NinjaAPI)
from savage_api.schemas import (
    UserLogin, PureText, Videoget, Videoin
)
from savage_api.models import (Video, Series)
from savage_api.uploader import (
   FileChunk, Uploader
)
from savage_api.exceptions import (
    InvalidHeader, InvalidQuery, UnexpetedRequest
)
from savage_api.response import UploadStatusResponse


api = NinjaAPI(version='dev')


# consts
no_response_body_set = frozenset({201, 204, 308})


@api.get("/video/{video_id}", response=Videoget, url_name='get_video')
def get_video(
    request,
    video_id: str
):
    """
        return the video stream url, should work with nginx
        set expire time for stream url, and it should sync with nginx
    """
    return {
        "status": "this method is not ready yet"
    }


@api.post("/video", url_name='post_video')  # add put method here
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
    # use cache instead
    request.session[upload_id] = session_data

    return {
        "status": "200",
        "upload_url": f"{reverse('api-dev:put_video')}?upload_id={upload_id}"
    }


# put should be Idempotent, use patch instead
@api.put("/video", response={no_response_body_set: None}, url_name='put_video')
def upload_video(request, upload_id: str):  # paramater resume is extra
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
    elif case == "error":
        return InvalidHeader(400)

    # start upload
    if case == "resume":
        uploader = Uploader.resume_upload(chunk)
    elif case == "new":
        uploader = Uploader.init_upload(chunk)
    uploader.receve_upload(chunk)


@api.get("/upload")
def upload_session_status(request):
    pass


@api.put("/upload", response={200: PureText})
def upload_video(request, upload_id=None):
    """
    Authorization: Bearer AUTH_TOKEN\n
    Content-Length: 524888\n
    Content-Type: video/*\n
    Content-Range: bytes 0-524287/2000000\n
    resume: resume request or not
    """
    session = request.session.get(upload_id)
    if session is None:
        return 404, {"status": "invalid upload id"}

    # validate pram list:
    #   resourse exist
    #   content range
    #   content size
    #   content extension
    #   chunk size

    if upload_id in request.session:  # 200
        chunk = FileChunk(request)
        uploader_file = UploaderFile.init_upload(upload_id, cache_conf='default')
        uploader_file.receve_upload(chunk)
        # save to db if upload complete
        return {
            "status": "200"
        }
    elif upload_id not in request.session:  # expire
        return 404, {"status": "upload id not found or session expire"}
    else:
        return UnexpetedRequest(status=404)


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
"""
exception register area
"""


@api.exception_handler(InvalidHeader)
def invalid_header(request, exc):
    return api.create_response(
        request,
        {
            "message": "Unexpected header",
            "detail": exc.message,
        },
        exc.status,
    )


@api.exception_handler(InvalidQuery)
def invalid_query(request, exc):
    return api.create_response(
        request,
        {
            "message": "Unexpected Query",
            "detail": exc.message,
        },
        exc.status,
    )


@api.exception_handler(UnexpetedRequest)
def unexpeted_request(request, exc):
    return api.create_response(
        request,
        {
            "message": "Unexpected Request"
        },
        exc.status
    )
