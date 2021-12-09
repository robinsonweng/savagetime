from ninja import NinjaAPI

api = NinjaAPI(version='0.1.0')


@api.get("/list/{series_id}")
def get_url_list():
    pass


@api.get("/upload")
def get_upload_session():
    pass


@api.get("/search")
def keyword_search():
    pass


@api.post("/athorize")
def user_athorizz():
    pass
