# view functions for authorize route

from ..libs.route import SavageRouter


authorize_router = SavageRouter()
authorize_router.prefix = "authorize/"


@authorize_router.api_operation(["GET"], "/")
def get_authorize():
    pass


@authorize_router.api_operation(["POST"], "/")
def post_authroize():
    pass
