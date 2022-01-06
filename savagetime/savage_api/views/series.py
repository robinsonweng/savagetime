# view functions for series router


from ninja import Router

from django.utils import timezone

from ..model.models import (
    Video, Series
)
from ..responses.exceptions import (
    InvalidHeader, InvalidQuery, UnexpetedRequest
)


series_router = Router()
series_router.prefix = "series/"
