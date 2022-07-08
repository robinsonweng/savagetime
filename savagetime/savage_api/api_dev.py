from ninja.constants import NOT_SET
from django.conf import settings

from .libs.savage import SavageAPI
from .utils.security import AdminUserBasicAuth

from .responses.exceptions import (
    InvalidHeader,
    InvalidQuery,
    UnexpetedRequest,
    UnsupportedMediaType,
)

from .responses.tus import TusHttpError

from .views import (
    video_router,
    series_router,
    search_router,
    authorize_router,
)

auth = AdminUserBasicAuth()
test_route = True
if getattr(settings, "IS_TESTING", None) is True:
    auth = NOT_SET
    test_route = True

api = SavageAPI(version='dev', auth=NOT_SET)


"""
    router register area
"""

api.add_router(video_router.prefix, video_router, tags=["video"])
api.add_router(series_router.prefix, series_router, tags=["series"])
api.add_router(search_router.prefix, search_router, tags=["search"])
api.add_router(authorize_router.prefix, authorize_router, tags=["authorize"])
if test_route:
    from .views.test import testroute
    api.add_router(testroute.prefix, testroute, tags=["testing"], auth=NOT_SET)


"""
    exception register area
"""


@api.exception_handler(InvalidHeader)
def invalid_header(request, exc):
    return api.create_response(
        request,
        data={
            "message": "Invalid or missing header",
            "detail": exc.message
        },
        status=exc.status
    )


@api.exception_handler(InvalidQuery)
def invalid_query(request, exc):
    return api.create_response(
        request,
        data={
            "message": "Unexpected Query",
            "detail": exc.message
        },
        status=exc.status,
    )


@api.exception_handler(UnexpetedRequest)
def unexpeted_request(request, exc):
    return api.create_response(
        request,
        data={
            "message": "Unexpected Request",
            "detail": exc.message
        },
        status=exc.status
    )


@api.exception_handler(UnsupportedMediaType)
def unsupported_media_type(request, exc):
    return api.create_response(
        request,
        data={
            "message": "Unsupported Media Type",
            "detial": exc.message
        },
        status=exc.status
    )


@api.exception_handler(TusHttpError)
def tus_error(request, exc):
    return api.create_response(
        request,
        data={
            "message": "Tus Uploader Error",
        },
        status=exc.status
    )