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
    FileChunk, UploaderFile
)
from savage_api.exceptions import (
    InvalidHeader, InvalidQuery, UnexpetedRequest
)


api = NinjaAPI(version='0.1.0')


@api.get("/video")
def get_video_url():
    pass


@api.post("/videos")  # add put method here
def create_video_metadata(request, metadata: Videoin, upload=False):
    """
    s: check if user login
    c: upload the metadata\n
        e.g.\n
        post /upload/youtube/v3/videos?uploadType=resumable&part=parts http/1.1\n
        host: www.googleapis.com\n
        authorization: bearer auth_token\n
        content-length: content_length\n
        content-type: application/json; charset=utf-8\n
        X-upload-content-length: x_upload_content_length\n
        X-Upload-Content-Type: X_UPLOAD_CONTENT_TYPE\n
    s: response an url for upload (with session id)\n
    if update interrupt then use head & patch (tus)\n


    """
    length_header = "X-upload-content-length"
    type_header = "X-upload-content-type"
    upload_content_length = request.headers.get(length_header)
    upload_content_type = request.headers.get(type_header)
    if not (upload_content_length is None) and not (upload_content_type is None):
        # also validate the user input
        request.session[length_header] = upload_content_length
        request.session[type_header] = upload_content_type
    elif (upload_content_length is None) and (upload_content_type is None):
        # return header missing error
        raise InvalidHeader(400, "Incorrect header or missing header value")

    if not Series.objects.filter(name=metadata.series_name).exists():
        return Http404({"status": "Video name not found"})
    if Video.objects.filter(episode=metadata.episode).exists():
        return Http404({"status": "Video already exist"})

    upload_id = None
    while (upload_id is None) or (upload_id in request.session):
        salt = os.urandom(5)  # generate salt for upload id
        upload_id = base64.b64encode(salt).decode()

    # init session
    request.session["upload_id"] = upload_id
    request.session["series"] = Videoin.series_name
    request.session["episode"] = Videoin.episode

    return {
        "status": "200",
        "upload_url": (  # multiple line string format
            "http://127.0.0.1:8000/api/dev/upload"
            f"?upload_id={upload_id}"
        ),
    }


@api.delete("/video")
def delete_video():
    pass


@api.get("/search")
def keyword_search():
    """
    text search in db
    """
    pass


@api.put("/series")
def update_series():
    """
        update series info
    """
    pass


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
