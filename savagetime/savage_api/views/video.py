# view functions for video route

import os
import uuid
import base64

from django.urls import reverse
from django.conf import settings
from django.http import (
    HttpResponseBadRequest, HttpResponseNotFound, HttpRequest

)
from django.core.cache import caches
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
    InvalidQuery, InvalidHeader, UnexpetedRequest, TusHttpError
)
from ..responses.response import (
    TusCoreResponse
)

from ..utils.tus_handler.tus import Chunk, TusUploader
from ..utils.tus_handler.extensions import (
    Creation, Termination, CheckSum, Expiration,
)
from ..utils.tus_handler import (
    tus_extensions, tus_resumable, tus_version, tus_max_size
)


no_response_body_set = frozenset({201, 204, 308})

video_router = SavageRouter()
video_router.prefix = "video/"  # set the root route

uploader_cache = caches[settings.RESUMEABLE_UPLOADER_CACHE_CONFIG]

"""




------------------ STREAM SECTION ----------------




"""
"""
TODO: Use pydantic to check headers, urls
"""


@video_router.api_operation(
    ["GET"],
    "/{video_id}/stream",
    response={200: dict},
    url_name="video_stream",
    auth=None,
)
def get_video_stream(request, video_id: str):
    ext = "m3u8"
    cdn = "127.0.0.2"
    base_stream = "index"
    md5 = "id2tPFIcl59pAG1kcorMig"
    # check if expire out of range
    # verify md5
    # md5 $path$ext
    # secure_link $md5$expire salt
    # echo -n '2147483647/s/link127.0.0.1 secret' | \
    # openssl md5 -binary | openssl base64 | tr +/ -_ | tr -d =
    return {"url": f"{cdn}/hls/123.mp4/{base_stream}.{ext}?md5={md5}"}


"""




------------------ UPLOAD SECTION ----------------




"""


@video_router.api_operation(["HEAD"], "/upload/{upload_id}/", url_name="tus_head")
def tus_head(request: HttpRequest, upload_id: str):
    """
        determine the offset at which the upload should be continued
        Warning: The md5 pram should be optional
    """
    resource_exist = TusUploader.resource_exist(upload_id)
    if not resource_exist:
        raise TusHttpError(status=404)
    offset = TusUploader.get_offset(upload_id)
    header = {
        "Tus-Extension": f"{tus_extensions}",
        "Tus-Resumable": f"{settings.TUS_RESUMABLE_VER}",
        "Tus-Max-Size": f"{settings.TUS_MAX_SIZE}",
        "Cache-Control": "no-store",
        "Upload-Offset": offset,
    }
    # upload metadata
    return TusCoreResponse(204, extra_headers=header)


@video_router.api_operation(["POST"], "/upload", response=NOT_SET, url_name="tus_post")
def tus_post(request, metadata: VideoUploadPostInput):
    """
        The Create extension
        Create resource for upload
    """
    series = Series.objects.filter(name=metadata.series_name)
    if not series.exists():
        return HttpResponseNotFound()
    if Video.objects.filter(episode=metadata.episode).exists():
        return HttpResponseBadRequest()

    chunk = Chunk(request)
    creation = Creation(chunk)

    creation.validate_header()
    creation.validate_metadata()
    creation.init_file_id()
    creation.init_cache(metadata.dict())

    header = {
        "Location":
            f'http://{request.get_host()}{reverse("api-dev:tus_patch", args=[creation.upload_id])}',
    }
    return TusCoreResponse(201, extra_headers=header)


@video_router.api_operation(
    ["PATCH"],
    "/upload/{upload_id}/",
    response={no_response_body_set: None, 200: dict},
    url_name="tus_patch"
)
def upload_video(request: HttpRequest, upload_id: str):
    """
        receives chunks to exist resource
        - check if resource exist(404)
        - Content-Type should be: application/offset+octet-stream(415)
        - validate the upload-offest(409)
        - validate the checksum (if avaliable)

    """
    resource_exist = TusUploader.resource_exist(upload_id)
    if resource_exist is False:
        raise TusHttpError(status=404)
    import sys
    sys.stderr.write(f"\n request header: {request.headers}\n")

    chunk = Chunk(request)
    uploader = TusUploader.start_upload(chunk, upload_id)

    uploader.validate()

    checksum = CheckSum(chunk)
    checksum.chunk_validate()

    current_offset = uploader.write_file()
    uploader.update_cache(current_offset)

    # uploader.clean()

    header = {
        "Upload-Offset": current_offset,
        "Tus-Resumable": "1.0.0"
    }
    return TusCoreResponse(status=204, extra_headers=header)


@video_router.api_operation(["DELETE"], "/upload/{upload_id}", response=NOT_SET, url_name="")
def clear_upload_session(request: HttpRequest, upload_id: str, delete_file: bool):
    """
        The delete extension
        delete the upload resource, the specify file, and the db data
        The standard behavior will be delete all the resource

        Load info from db, then delete local, db data
        clean cache if data exsist
    """
    if not upload_id:
        return TusHttpError(400)

    termination = Termination(request)
    termination.clear_cache(upload_id)

    # cache
    # database
    # local


@video_router.api_operation(["OPTION"], "/upload", response=NOT_SET, url_name="")
def upload_option(request: HttpRequest):
    """
        204
        200
        header: must contain Tus-Version, may include Tus-Extension and Tus-Max-Size
        COROs?
    """
    headers = {
        "Tus-Resumable": f"{tus_resumable}",
        "Tus-Version": f"{tus_version}",
        "Tus-Max-Size": f"{tus_max_size}",
        "Tus-Extension": f"{tus_extensions}"
    }
    return TusCoreResponse(204, headers)


"""




------------------ INFO SECTION ----------------




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
    """
        not sure this should exist
    """
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
            series = Series.objects.get(name=series_name)  # noqa: F841
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(None, 404)
        except ValidationError:
            return HttpResponseBadRequest(None, 400)
    else:
        return HttpResponseBadRequest(None, 400)
    return HttpRequest(201)


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
    return HttpRequest(201)  # created


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
    return HttpRequest(201)


"""




------------------ SERIES SECTION ----------------




"""


@video_router.api_operation(["GET"], "{video_id}/series", auth=None)
def get_series_from_video(request, video_id: str):
    pass
