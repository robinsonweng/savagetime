from typing import TypeVar, Type, List
from ninja.errors import HttpError
from django.core.cache import caches
from django.http import HttpResponse
from django.conf import settings
from savage_api.exceptions import (
    InvalidHeader, InvalidQuery
)

Chunk = TypeVar('Chunk', bound="FileChunk")
Uploader = TypeVar('Uploader', bound="UploaderFile")
