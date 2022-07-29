from django.conf import settings
from django.core.cache import caches


# cache
tus_cache = caches[settings.TUS_CACHE_CONF]
# cache keys
metadata_key = lambda upload_id: f"uploader/{upload_id}/metadata"  # noqa: E731
offset_key = lambda upload_id: f"uploader/{upload_id}/offset"  # noqa: E731
file_size_key = lambda upload_id: f"uploader/{upload_id}/filesize"  # noqa: E731
filename_key = lambda upload_id: f"uploader/{upload_id}/filename"  # noqa: E731
