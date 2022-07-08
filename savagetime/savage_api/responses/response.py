# Write custom http response & header here
from django.http import HttpResponse


class ResponseHeaderBase(HttpResponse):
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


class UploadStatusResponse(ResponseHeaderBase):
    # 308, not a standard http code usage
    _base_headers = {
        'Content-Length': 0,
        'Content-Range': "",
    }


class NoBodyResponse(ResponseHeaderBase):
    pass
