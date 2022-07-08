from typing import Callable
from django.http import HttpRequest
from django.urls import reverse
from django.core.files.uploadedfile import UploadedFile, TemporaryUploadedFile


class TusMiddleware(object):
    def __init__(self, get_response: Callable):
        """
            the get_response could be the next middleware or acsual view function
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpRequest:
        response = self.get_response(request)
        return response
