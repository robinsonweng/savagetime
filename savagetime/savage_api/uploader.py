import os
import re
import uuid
from pathlib import Path
from typing import TypeVar, Type, List  # typing is too chaotic
# from ninja.errors import HttpError
from django.core.cache import caches
from django.http import HttpRequest
from django.conf import settings


Chunk = TypeVar('Chunk', bound="FileChunk")
Uploader = TypeVar('Uploader', bound="Uploader")

# cache keys
file_size_key = lambda upload_id: f"uploadfile/{upload_id}/file_size"  # noqa: E731
metadata_key = lambda upload_id: f"uploadfile/{upload_id}/metadata"  # noqa: E731
cursor_key = lambda upload_id: f"uploadfile/{upload_id}/cursor"  # noqa: E731
file_name_key = lambda upload_id: f"uploadfile/{upload_id}/file_name"  # noqa: E731

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

    @classmethod
    def load_chunk(cls, request: Type[HttpResponse]) -> Type[Chunk]:
        return cls(request)

    @property
    def byte_start(self) -> HttpError:
        try:
            value = self.chunk_range.split(" ")[1].split("/")[0].split("-")[0]
            int(value)
        except ValueError:  # what if value missing '/' or '-'
            raise InvalidHeader(400, "Incorrect header value from Content-Range")
        return value

    @property
    def byte_end(self) -> HttpError:
        try:
            value = self.chunk_range.split(" ")[1].split("/")[0].split("-")[1]
            int(value)
        except ValueError:
            raise InvalidHeader(400, "Incorrect header value from Content-Range")
        return value

    @property
    def content_length(self) -> HttpError:
        try:
            value = self.chunk_range.split(" ")[1].split("/")[1]
            int(value)
        except ValueError:
            raise InvalidHeader(400, "Incorrect header value from Content-Range")
        return value


class UploaderFile(object):
    def __init__(self, upload_id: str, cache_conf: str) -> None:
        try:
            caches[cache_conf]
        except KeyError:
            raise KeyError("Cache setting not found")

        self.cache_conf = cache_conf
        self.upload_id = upload_id
        self.file_size = int(caches[cache_conf].get(f"uploadfile/{upload_id}/file_size"))
        self.file_name = caches[cache_conf].get(f"uploadfile/{upload_id}/file_name")
        self.metadata = caches[cache_conf].get(f"uploadfile/{upload_id}/metadata")
        self.cursor = caches[cache_conf].get(f"uploadfile/{upload_id}/cursor")

    @staticmethod
    def resource_exist(cache_conf: str, upload_id: str) -> bool:
        return (caches[cache_conf].get(f"uploadfile/{upload_id}/file_name") is not None)

    @staticmethod
    def valid_file_size(file_size: int, chunk_length) -> bool:
        if file_size != chunk_length:
            return False
        return True

    @staticmethod
    def valid_init_upload_param() -> None:
        if UploaderFile.resource_exist() is True:
            raise InvalidQuery(400, "This session already start an upload")
