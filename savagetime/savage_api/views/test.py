from django.http import HttpRequest
from django.urls import reverse
from django.conf import settings
from django.dispatch.dispatcher import receiver

from ninja.files import UploadedFile
from ninja import File

from ..libs.route import SavageRouter
from ..model.models import Video, Series

from ..responses.exceptions import TusHttpError
from ..responses.response import TusCoreResponse

from ..utils.tus_handler.middlewares import (
    detect_offset_stream,
)

from ..utils.tus_handler.tus import Chunk, TusUploader

from ..utils.tus_handler.extensions import tus_protocol_extensions
from ..utils.tus_handler.extensions import Creation


testroute = SavageRouter()
testroute.prefix = "test/"

"""
    Core tus protocol
"""


@testroute.api_operation(["HEAD"], "/{file_md5}/", auth=None, url_name="test")
def tus_head(request: HttpRequest, file_md5: str):
    """
        determine the offset at which the upload should be continued
        Warning: The md5 pram should be optional
    """
    resource_exist = TusUploader.resource_exist(file_md5)
    if not resource_exist:
        raise TusHttpError(status=404)
    offset = TusUploader.get_offset(file_md5)
    header = {
        "Tus-Extension": f"{tus_protocol_extensions}",
        "Tus-Resumable": f"{settings.TUS_RESUMABLE_VER}",
        "Tus-Max-Size": f"{settings.TUS_MAX_SIZE}",
        "Cache-Control": "no-store",
        "Upload-Offset": offset,
    }
    # upload metadata
    return TusCoreResponse(204, extra_headers=header)


@testroute.api_operation(
    ["PATCH"],
    "/{file_md5}/",
    auth=None,
    before_request=[],
)
def tus_patch(request: HttpRequest, file_md5: str):
    """
        receives chunks to exist resource
        - check if resource exist(404)
        - Content-Type should be: application/offset+octet-stream(415)
        - validate the upload-offest(409)
        - validate the checksum (if avaliable)

    """
    resource_exist = TusUploader.resource_exist(file_md5)
    if resource_exist is False:
        raise TusHttpError(404)

    print("--------------------------------------------------")
    chunk = Chunk(request)
    uploader = TusUploader.start_upload(chunk, file_md5)

    # validate offset
    # validate chunk length
    uploader.validate()

    # receve chunks
    current_offset = uploader.receve_chunks()
    uploader.clean()

    # update cache
    # clean cache
    header = {
        "Upload-Offset": current_offset,
    }
    return TusCoreResponse(204, extra_headers=header)  # successful


@testroute.api_operation(["OPTIONS"], "/", auth=None, before_request=[])
def tus_options(request: HttpRequest, file_md5: str = ""):
    """
        Gather information about the server's current configuration,
        may include the Tus-Extension and Tus-Max-Size
        - response header MUST contain Tus-Version header
        - response header may include Tus-Extension, Tus-Max-Size
        - Clinet SHOULD NOT include Tus-Resumable header and Server
        MUST ignore the header
    """
    header = {
        "Tus-Resumable": "1.0.0",
        "Tus-Version": "1.0.0",
        "Tus-Max-Size": "1073741824",
        "Tus-Extension": "creation",
    }
    return TusCoreResponse(204, extra_headers=header)


"""
    Tus protocol extension
"""


@testroute.api_operation(["POST"], "/", auth=None)
def tus_post(request: HttpRequest):
    """
        Create resource for upload\n
        if already exist ?
    """

    chunk = Chunk(request)
    creation = Creation(chunk)

    creation.validate_header()
    creation.validate_metadata()
    creation.init_file_id()
    creation.init_cache()

    header = {
        "Location": f'http://{request.get_host()}{reverse("api-dev:test", args=[creation.upload_id])}',
    }
    return TusCoreResponse(201, extra_headers=header)


@testroute.api_operation(["DELETE"], "/", auth=None)
def tus_delete(request: HttpRequest):
    """"""
