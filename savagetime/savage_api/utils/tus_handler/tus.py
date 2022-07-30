import os

from django.http import HttpRequest
from django.conf import settings

from ..tus_handler import (
    tus_cache,
    metadata_key,
    offset_key,
    file_size_key,
    filename_key,
)


class Chunk(object):
    """
        HttpRequest Parser
    """
    def __init__(self, request: HttpRequest):
        self.META = request.META
        self.data = request.body
        self.headers = request.headers

    def __getitem__(self, key) -> dict:
        return self.META.get(key)


class TusUploader(object):
    """
        Basic uploader for patch method
    """
    def __init__(self, chunk: Chunk, upload_id: str) -> None:
        self.chunk = chunk
        self.upload_id = upload_id
        self.temp_filename = f"{upload_id}.temp"

        # cache var
        self.cache_offset = int(tus_cache.get(offset_key(upload_id), None))
        self.cache_length = int(tus_cache.get(file_size_key(upload_id), None))
        self.cache_metadata = tus_cache.get(metadata_key(upload_id), None)
        self.cache_filename = tus_cache.get(filename_key(upload_id), None)

        # chunk var
        self.chunk_offset = int(self.chunk.headers.get("Upload-Offset"))
        self.chunk_length = int(self.chunk.headers.get("Content-Length"))
        self.chunk_contentlen = self.chunk.headers.get("Upload-Length")

    @classmethod
    def start_upload(cls, chunk: Chunk, upload_id: str) -> object:
        uploader = cls(chunk, upload_id)
        if uploader.dir_exist() is False:
            raise ValueError(f"dir: {settings.FILE_UPLOAD_TEMP_DIR} is not a path")
        if uploader.file_exist() is False:
            print("new file")
            uploader.init_file()
        return uploader

    @staticmethod
    def resource_exist(upload_id: str) -> bool:
        """
            seek resource status
        """
        local_file = tus_cache.get(metadata_key(upload_id), None)
        if local_file is None:
            return False
        return True

    @staticmethod
    def get_offset(upload_id: str) -> int:
        offset = tus_cache.get(offset_key(upload_id), None)
        return offset

    def validate(self) -> None:
        """
            validate all require pramaters
        """

        # validate offset
        client_offset = self.chunk.headers.get("Upload-Offset", None)
        if not (client_offset and self.cache_offset):
            return  # header missing

        if str(client_offset) != str(self.cache_offset):
            return  # offset conflict

    def file_exist(self) -> bool:
        """
            seek if file exist
        """
        if os.path.isfile(os.path.join(settings.FILE_UPLOAD_TEMP_DIR, self.temp_filename)):
            return True
        return False

    def init_file(self) -> None:
        """
            initialize file in local
        """
        with open(os.path.join(settings.FILE_UPLOAD_TEMP_DIR, self.temp_filename), "wb") as f:
            print(f"init offset: {f.tell()}")
            print(f"init cache offset: {self.cache_offset}")
            f.seek(self.cache_length)
            print(f.tell())

    def write_file(self) -> int:
        """
            write chunks into file
        """
        with open(os.path.join(settings.FILE_UPLOAD_TEMP_DIR, self.temp_filename), "rb+") as f:
            # print(f"cache offset: {self.cache_offset}")
            # print(f"chunk offset: {self.chunk_offset}")
            f.seek(self.cache_offset)
            # print(f"start writing: {f.tell()}")
            f.write(self.chunk.data)
            # print(f"offset after writing: {f.tell()}")
            return f.tell()

    def dir_exist(self):
        """
            check if dir exist
        """
        return os.path.isdir(settings.FILE_UPLOAD_TEMP_DIR)

    def is_complete(self) -> bool:
        """
            return true if complete
        """

    def update_cache(self, current_offset: int):
        """
            update cache status
        """
        tus_cache.incr(offset_key(self.upload_id), len(self.chunk.data))

    def clean(self, option="cache"):
        """
            clean the temporary file or cache
        """

    def run(self):
        print(self.chunk_offset)
        print(self.cache_offset)
