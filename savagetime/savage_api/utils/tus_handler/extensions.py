import base64
import hashlib
from hmac import compare_digest

from django.conf import settings
from django.core.cache import caches

from ninja.errors import HttpError

from .tus import Chunk, TusUploader
from ..tus_handler import (
    tus_cache,
    offset_key,
    metadata_key,
    file_size_key,
    filename_key,
    schema_key,
)


tus_protocol_extensions = ["creation"]


class Creation(object):
    """
        Create a new upload resource
        - Server and Client SHOULD implment this extension
        - MUST add header Tus-Extension: creation in OPTION request
    """
    def __init__(self, chunk: Chunk) -> None:
        self.chunk = chunk

    def validate_header(self) -> None:
        """
        - The Client may supply the Upload-Metadata header to add additional metadata,
        the Sever should decide to ignore or use, or reject.
        - Upload-Length
            Once set this header, the value MUST NOT change.

        """
        upload_length = self.chunk.headers.get("Upload-Length", None)
        if upload_length is None:
            raise HttpError(status_code=400)

        try:
            int(upload_length)
        except ValueError:
            raise HttpError(status_code=400)

        if int(upload_length) > int(settings.TUS_MAX_SIZE):
            raise HttpError(status_code=413)

        if int(upload_length) < 0:
            raise HttpError(status_code=400)

        meta = self.chunk.headers.get("Upload-Metadata", None)
        if meta is None:
            raise HttpError(status_code=400)
        self._metadata = meta

    def validate_metadata(self):
        """
            value should be base64
            key should be ascii
            key: filename, filetype
            carefully validate metadata values or sanitize them
        """
        data = {}
        for meta in self._metadata.split(","):
            s = meta.split(" ")
            if len(s) == 1:
                data[s[0]] = None
            elif len(s) == 2:
                data[s[0]] = s[1]

        if "filename" not in data or "filetype" not in data:
            pass  # 400
        self.metadata = self._metadata

    def validate_request_id(self):
        """
            check if id is uuid4
        """

    def init_file_id(self) -> None:
        byte = self.metadata.encode("utf-8")
        md5 = hashlib.md5(byte).hexdigest()
        self.upload_id = md5

    def init_cache(self, metadata: dict) -> None:
        """
            initialize data into cache
        """
        tus_cache.set(metadata_key(self.upload_id), self.metadata)
        tus_cache.set(offset_key(self.upload_id), 0)
        tus_cache.set(file_size_key(self.upload_id), self.chunk.headers.get("Upload-Length"))
        tus_cache.set(filename_key(self.upload_id), self.upload_id)  # this should change as filename
        tus_cache.set(schema_key(self.upload_id), metadata)


class CreationWithUpload(object):
    """
        Extension for post method, start upload after create resource with out patch method
    """
    pass


class Termination(object):
    """
        delete the current resource
        204
        404
        410
    """
    def __init__(self, chunk: Chunk):
        pass

    def termination_header_valid(self):
        pass

    def delete_local_resource(self):
        pass

    def delete_file_db_info(self):
        pass

    def clear_cache(self, upload_id: str):
        tus_cache.delete(metadata_key(upload_id))
        tus_cache.delete(offset_key(upload_id))
        tus_cache.delete(file_size_key(upload_id))
        tus_cache.delete(filename_key(upload_id))


class Expiration(object):
    """
        Indicate the expire time after upload finish
        204
        404
        410
        Set expiration for cache, but how about temp files?
    """
    pass


class CheckSum(object):
    """
        validate the file after the upload is complete
        the header Tus-Checksum-Algorithm should include in OPTIONS response
        the header Upload-Checksum MAY include in every PATCH request
        the algo is not supported by the server(400)
        if the checksum is mismatch(460)
        succeeded(200)
    """
    def __init__(self, chunk: Chunk) -> None:
        algo_list = ["sha1", "sha2"]
        header = chunk.headers.get("Upload-Checksum").split(" ")

        self.header_checksum = header[1]
        self.algo = header[0]
        self.data = chunk.data

        if self.algo not in algo_list:
            raise HttpError(status_code=460, message="unsupported checksum algorithm")

    def chunk_validate(self) -> None:
        """
            if chunk checksum != header checksum(460)
        """
        chunk_checksum = hashlib.new(self.algo)
        chunk_checksum.update(self.data)
        chunk_checksum = base64.b64encode(chunk_checksum.digest()).decode("utf-8")

        if not compare_digest(self.header_checksum, chunk_checksum):
            raise HttpError(status_code=460, message="checksum mismatch")

    def finish_validate(self):
        """
            validate file after finish upload
        """
        pass

    def checksum_trailer(self):
        pass
