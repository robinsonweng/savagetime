from ninja import NinjaAPI

api = NinjaAPI(version='0.1.0')


@api.get("/hello")
def hello(request):
    return "Hello world"
