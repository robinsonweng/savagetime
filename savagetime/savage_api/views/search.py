# view functions for search router

from ninja import Router


search_router = Router()
search_router.prefix = "search/"


@search_router.api_operation(["GET"], "/")
def get_search_result(request, keyword: str):
    pass
