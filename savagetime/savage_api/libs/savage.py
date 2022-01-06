from ninja import NinjaAPI

from .route import SavageRouter


class SavageAPI(NinjaAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
