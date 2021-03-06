# view functions for series router

from typing import List

from django.utils.encoding import smart_str
from django.utils import timezone

from ninja.constants import NOT_SET
from ..libs.route import SavageRouter


from ..model.models import (
    Video, Series
)
from ..model.schemas.video import (
    VideoInfo
)
from ..model.schemas.series import (
    SeriesInfoOutput, SeriesInfoPostInput, SeriesInfoPatchInput
)

from ..responses.exceptions import (
    InvalidHeader, InvalidQuery, UnexpetedRequest
)


series_router = SavageRouter()
series_router.prefix = "series/"


"""
    series/{series_id}/info sections
"""


@series_router.api_operation(
    ["GET"],
    "/info",
    response=List[VideoInfo],
    url_name="",
    auth=None,
)
def get_series_info(
    request,
    series_id: str = None,
    index: str = None,
    recent: bool = False,
):
    """
        this route return the urls of the video, not streaming
        url from nginx\n
        @series_id: the uuid of the series\n
        @index: the range of the video episodes, e.g. 1-2 means\n
        episode 1 and 2, the amound of video shouldn't exceed 30\n
        @recent: if true, return the recent updated videos(1d)\n
    """
    id_exist = series_id is not None
    index_exist = index is not None
    if (recent is True) and not (id_exist and index_exist):
        # ^ if client expected recent update video
        today = timezone.now()
        recent = Video.objects.filter(
            # use 24h instead
            update_time__date=today.date()
        )

        return recent
    elif (not recent) and (id_exist and index_exist):
        # ^ if client expected query video using index & series id
        pass
    else:
        raise InvalidQuery(400, "")


@series_router.api_operation(["POST"], "/info", response={201: SeriesInfoOutput}, url_name="")
def post_series_info(request, data: SeriesInfoPostInput, index: str = None):
    series = Series(
        name=data.name,
        season=data.season,
        episodes=data.episodes,
        pub_year=data.pub_year,
        pub_month=data.pub_month,
        finale=data.finale,
        subtitle_group=data.subtitle_group,
    )
    series.save()
    return 201, series  # created


@series_router.api_operation(
    ["PATCH"],
    "{series_id}/info",
    response={204: SeriesInfoOutput},
    url_name="")
def patch_series_info(request, series_id: str, data: SeriesInfoPatchInput):
    series = Series.objects.get(uuid=series_id)

    for data_attr in SeriesInfoPatchInput.__dict__["__fields__"]:
        value = getattr(data, data_attr)
        if (data_attr == "finale") and (value is not False):
            setattr(series, "finale", True)
        elif value is not None:
            setattr(series, data_attr, value)

    series.save()
    return 204, series


@series_router.api_operation(["DELETE"], "{series_id}/info", response=NOT_SET, url_name="")
def delete_series_info(request, series_id: str):
    series = Series.objects.get(uuid=series_id)
    series.delete()
    return NoBodyResponse(None, 204)
