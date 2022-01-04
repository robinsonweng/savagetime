# Write custom http response & header here
from django.http import HttpResponse


class ResponseHeaderBase(HttpResponse):
    _base_headers = {
    }

    def add_header(self, header: dict):
        for k, v in header.items():
            self.__setitem__(k, v)

    def __init__(self, extra_headers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_header(self._headers)

        if extra_headers is not None:
            if isinstance(extra_headers, dict):
                self.add_header(extra_headers)
            else:
                raise ValueError("param: extra_header should be dict")


class UploaderResponse(ResponseHeaderBase):
    _base_headers = {
        ''
    }


class UploadStatusResponse(ResponseHeaderBase):
    # 308, not a standard http code usage
    _headers = {
        'Content-Length': 0,
        'Content-Range': "",
    }
