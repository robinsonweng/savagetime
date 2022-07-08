# Create exceptions here
from ninja.errors import HttpError


class HttpErrorBase(HttpError):
    def __init__(self, status, message):
        self.status = status
        self.message = message

class InvalidHeader(HttpError):
    def __init__(self, status, message="None"):
        self.status = status
        self.message = message


class InvalidQuery(HttpError):
    def __init__(self, status, message="None"):
        self.status = status
        self.message = message


class UnexpetedRequest(HttpError):
    pass


class UnsupportedMediaType(HttpErrorBase):
    def __init__(self, message, status=415):
        super().__init__(status, message)
