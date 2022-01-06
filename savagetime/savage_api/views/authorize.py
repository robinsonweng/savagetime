# view functions for authorize route

from ninja import Router


authorize_router = Router()
authorize_router.prefix = "authorize/"


@authorize_router.api_operation(["GET"], "/")
def get_authorize():
    pass


@authorize_router.api_operation(["POST"], "/")
def post_authroize():
    pass
