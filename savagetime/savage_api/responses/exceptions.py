# Create exceptions here
from ninja.errors import HttpError


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
