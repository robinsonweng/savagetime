# view functions for search router

from ..libs.route import SavageRouter


search_router = SavageRouter()
search_router.prefix = "search/"


@search_router.api_operation(["GET"], "/")
def get_search_result(request, keyword: str):
    pass
