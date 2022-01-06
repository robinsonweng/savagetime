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


"""
    series/{series_id}/info sections
"""


@series_router.api_operation(["GET"], "{series_id}/info")
def get_series_info(request, series_id: str, index: str, recent: bool = False):
    """
        this route return the urls of the video, not streaming
        url from nginx
        @series_id: the uuid of the series
        @index: the range of the video episodes, e.g. 1-2 means
        episode 1 and 2, the amound of video shouldn't exceed 30
        @recent: if true, return the recent updated videos(1d)
    """
    id_exist = series_id is not None
    index_exist = index is not None
    recent_exist = recent is not None
    if (recent is True) and not (id_exist and index_exist):
        # if client expected recent update video
        today = timezone.now()
        recent = Video.objects.filter(
            # use 24h instead
            update_time__date=today.date()
        )
        v_list = []
        from django.utils.encoding import smart_str
        for video in recent:
            v_list.append(smart_str(video.series.name))

        return {"status": f"{v_list}"}
    elif (not recent_exist) and (id_exist and index_exist):
        # if client query video using index & series id
        pass
    else:
        raise InvalidQuery(400, "")
