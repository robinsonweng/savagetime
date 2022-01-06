from .libs.savage import SavageAPI

from .responses.exceptions import (
    InvalidHeader,
    InvalidQuery,
    UnexpetedRequest,
)

from savage_api.views import (
    video_router,
    series_router,
    search_router,
)




















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
