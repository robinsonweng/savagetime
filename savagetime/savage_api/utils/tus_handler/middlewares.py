from django.http import HttpRequest
from django.urls import reverse
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler 

from savage_api.responses.exceptions import UnsupportedMediaType


def detect_offset_stream(request: HttpRequest, *args, **kwargs):
    """
        check if content-type is valid
    """
    content_type = request.headers.get("content-type", None)
    if content_type != "application/offset+octet-stream":
        raise UnsupportedMediaType()


