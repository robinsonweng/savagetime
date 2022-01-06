from .libs.savage import SavageAPI

from .responses.exceptions import (
    InvalidHeader,
    InvalidQuery,
    UnexpetedRequest,
)

from .views import (
    video_router,
    series_router,
    search_router,
    authorize_router,
)


api = SavageAPI(version='dev')


"""
    router register area
"""

api.add_router(video_router.prefix, video_router, tags=["video"])
api.add_router(series_router.prefix, series_router, tags=["series"])
api.add_router(search_router.prefix, search_router, tags=["search"])
api.add_router(authorize_router.prefix, authorize_router, tags=["authorize"])


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
