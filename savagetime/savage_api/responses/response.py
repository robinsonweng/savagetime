# Write custom http response & header here
from django.http import HttpResponse


class ResponseHeaderBase(HttpResponse):  # what is this stupid name
    _base_headers = {}
    # ^ general header, e.g. CORS

    def add_header(self, header: dict):
        for k, v in header.items():
            self.__setitem__(k, v)

    def __init__(self, status=None, extra_headers={}, *args, **kwargs):
        super().__init__(status=status, *args, **kwargs)
        self.add_header(self._base_headers)

        if extra_headers is not None:
            if isinstance(extra_headers, dict):
                if extra_headers:
                    # ^ if dict is not empty
                    self.add_header(extra_headers)
            else:
                raise ValueError(f"param: extra_header should be dict, got {extra_headers} instead")


class TusCoreResponse(ResponseHeaderBase):
    _base_headers = {
        "Tus-Version": "1.0.0",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Request-Method": "GET,POST,PATCH,OPTIONS,HEAD",
        "Access-Control-Allow-Headers": "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset,content-type",
        "Access-Control-Expose-Headers": "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset",
    }
