import os
import re
import uuid
import base64
import hashlib

from pathlib import Path
from hmac import compare_digest

from django.core.cache import caches
from django.conf import settings

from ..responses.exceptions import InvalidHeader

# typing
from typing import TypeVar, Type, List
from django.http import HttpRequest, HttpResponse
Uploader = TypeVar("Uploader", bound="Uploader")
FileChunk = TypeVar("FileChunk", bound="FileChunk")


# const init
cache = caches[settings.RESUMEABLE_UPLOADER_CACHE_CONFIG]
dest_dir = settings.RESUMEABLE_UPLOADER_DEST_PATH

# cache keys
file_size_key = lambda upload_id: f"uploader/{upload_id}/file_size"  # noqa: E731
metadata_key = lambda upload_id: f"uploader/{upload_id}/metadata"  # noqa: E731
cursor_key = lambda upload_id: f"uploader/{upload_id}/cursor"  # noqa: E731
file_name_key = lambda upload_id: f"uploader/{upload_id}/file_name"  # noqa: E731


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
        return int(value)

    @property
    def byte_end(self) -> str:
        value = self.range.split(" ")[1].split("/")[0].split("-")[1]
        return int(value)

    @property
    def content_length(self) -> str:
        value = self.range.split(" ")[1].split("/")[1]
        return int(value)


class Uploader(object):
    def __init__(self, upload_id: str) -> None:
        # constant
        self.upload_id = upload_id
        self.is_complete = False

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
    def get_progress(upload_id):
        # should caculate from actsual file
        cursor = cache.get(cursor_key(upload_id), None)
        if cursor is not None:
            return cursor.split(" ")[1]

    def create_file(self, file_path: str) -> None:
        """
            create blank file
        """
        dir_path = Path(file_path).parent
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        try:
            with open(file_path, 'wb') as f:
                f.seek(self.file_size - 1)
                f.write(b'\0')  # EOF
        except IOError:
            raise IOError("Error occor while createing file")

    def write_file(self, path, chunk):
        try:
            with open(path, "rb+") as f:
                f.seek(int(chunk.byte_start))
                f.write(chunk.binary)
        except IOError:
            raise IOError("Error occor while writing file")

    @classmethod
    def init_upload(
        cls: Uploader, upload_id: str, metadata, chunk: Type[FileChunk]
    ) -> Type[Uploader]:
        """
            1. Validate param from user\n
            2. create blank file in local\n
            3. return self\n
        """
        series_id = metadata["series_id"]
        video_uuid = uuid.uuid4()
        video_uuid = str(video_uuid)
        video_name = os.path.join(series_id, video_uuid)

        path = f"{os.path.join(Uploader.get_dest_dir(), video_name)}.mp4"

        cache.add(file_size_key(upload_id), chunk.content_length)
        cache.add(metadata_key(upload_id), metadata)
        cache.add(cursor_key(upload_id), chunk.range)
        cache.add(file_name_key(upload_id), f"{video_name}.mp4")

        uploader = cls(upload_id)
        uploader.valid_init_upload_param()  # check pram
        # init file
        uploader.create_file(path)
        return uploader

    @classmethod
    def resume_upload(cls, upload_id) -> Type[Uploader]:
        uploader = cls(upload_id)
        uploader.valid_resume_upload_param()
        return uploader

    def get_metadata(self):
        return self.metadata

    def receve_upload(self, chunk: Type[FileChunk]) -> None:
        """
            1. valid param from user\n
            2. write chunks from cache to local file\n
        """
        path = os.path.join(self.get_dest_dir(), self.file_name)
        self.write_file(path, chunk)
        if self.file_size == chunk.byte_end:
            self.is_complete = True
        # update cache cursor
        # validate cursor

    def flush(self, option="cache"):
        """
            clear cache or local
        """
        options = ["cache", "local", "all"]
        if option not in options:
            raise ValueError(
                f"Paramater 'option' only accept value 'cache', "
                f"'local', 'all', but get {option} instead"
            )

        if option == "cache" or option == "all":
            cache.delete(file_size_key(self.upload_id))
            cache.delete(metadata_key(self.upload_id))
            cache.delete(cursor_key(self.upload_id))
            cache.delete(file_name_key(self.upload_id))

        if option == "local" or option == "all":
            path = os.path.join(self.get_dest_dir(), self.file_name)
            try:
                os.remove(path)
            except FileNotFoundError as e:
                raise e(f"file: '{path}' not found")

    def verify_checksum(self, checksum: str, option="sha256"):
        algo = ["sha256"]
        if option not in algo:
            raise ValueError(f"key word arg 'option' only accept {algo}, get '{option}' instead")

        my_check = hashlib.new(option)
        with open(os.path.join(self.get_dest_dir(), self.file_name), "rb") as f:
            my_check.update(f.read())
        my_check = base64.b64encode(my_check.digest()).decode()
        return compare_digest(my_check, checksum)

    def valid_init_upload_param(self) -> None:
        # init valid pram list:
        #   byte_start should startwith 0
        #   byte_start should not equal to byte_end
        #   content
        pass

    def valid_resume_upload_param(self) -> None:
        # validate pram list:
        #   resourse exist
        #   content range
        #   content size
        #   content extension
        #   chunk size
        pass
