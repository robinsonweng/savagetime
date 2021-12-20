from typing import TypeVar, Type, List
from ninja.errors import HttpError
from django.core.cache import caches
from django.http import HttpResponse
from django.conf import settings
from savage_api.exceptions import (
    InvalidHeader, InvalidQuery
)

Chunk = TypeVar('Chunk', bound="FileChunk")
Uploader = TypeVar('Uploader', bound="UploaderFile")


class FileChunk(object):
    def __init__(self, request) -> None:
        self.chunk_length = request.headers.get("Content-Length")
        self.chunk_type = request.headers.get("Content-Type")
        self.chunk_range = request.headers.get("Content-Range")
        self.chunk = request.body
        self.check_headers()

    def check_headers(self) -> None:
        if (self.chunk_length is None) or (self.chunk_type is None) or (self.chunk_range is None):
            raise InvalidHeader(400, "Incorrect header or missing header value")
