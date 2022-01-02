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
    def __init__(self, request: HttpRequest) -> None:
        # request field
        self.headers = request.headers  # dont use META if the use case is for header
        self.length = request.headers.get("Content-Length")
        self.type = request.headers.get("Content-Type")
        self.range = request.headers.get("Content-Range")
        self.binary = request.body

    @classmethod
    def load_chunk(cls, request: HttpRequest) -> Type[Chunk]:
        chunk = cls(request)
        return chunk

    # maby use regex instead of split
    def get_case(self):
        range_math = re.match(r"bytes \*\/\d+", self.range)

        if range_math is not None and len(self.binary) == 0:  # status
            return "status"
        elif self.byte_start == 0:
            return "new"
        elif self.byte_start > 0:
            return "resume"
        return "error"  # error

    @property
    def byte_start(self) -> str:
        # filter this from nginx, probably change to regex
        value = self.range.split(" ")[1].split("/")[0].split("-")[0]
        return value

    @property
    def byte_end(self) -> str:
        value = self.range.split(" ")[1].split("/")[0].split("-")[1]
        return value

    @property
    def content_length(self) -> str:
        value = self.range.split(" ")[1].split("/")[1]
        return value


class Uploader(object):
    def __init__(self, upload_id: str) -> None:
        # constant
        self.upload_id = upload_id
        self.cache_conf = settings.RESUMEABLE_UPLOADER_CACHE_CONFIG
        try:
            cache = caches[self.cache_conf]
        except KeyError:
            raise KeyError("Cache setting not found")
        # init data from cache
        self.file_size = int(cache.get(file_size_key(upload_id), None))
        self.file_name = cache.get(file_name_key(upload_id), None)
        self.metadata = cache.get(metadata_key(upload_id), None)
        self.cursor = cache.get(cursor_key(upload_id), None)

    @staticmethod  # maby use cached_property?
    def get_dest_dir():
        return settings.RESUMEABLE_UPLOADER_DEST_PATH

    @staticmethod
    def resource_exist(upload_id: str, cache_conf: str) -> bool:
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
