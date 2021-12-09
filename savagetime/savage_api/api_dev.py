from ninja import NinjaAPI

api = NinjaAPI(version='0.1.0')


@api.get("/video")
def get_video_url():
    pass


@api.post("/video")
def post_upload_metadata():
    """
    c: upload the metadata
    s: response an url for upload
    if interrupt then use head & patch (tus)
    """
    pass


@api.put("/video")
def modify_video():
    pass


@api.delete("/video")
def delete_video():
    pass


@api.get("/search")
def keyword_search():
    """
    text search in db
    """
    pass


@api.get("/authorize")
def get_user_athorize():
    """
    return user authorize status
    """
    pass


@api.post("/authorize")
def post_user_athorize():
    """
    route for user authorizing
    """
