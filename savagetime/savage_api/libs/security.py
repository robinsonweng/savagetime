from typing import Optional, Any

from ninja.security import HttpBasicAuth
from ninja.errors import HttpError

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist


class AdminUserBasicAuth(HttpBasicAuth):
    def authenticate(self, request: HttpRequest, username: str, password: str) -> Optional[Any]:
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise HttpError(403, "Password or Username incorrect")
        if user.check_password(password) is False:
            # if password incorrect
            raise HttpError(403, "Password or Username incorrect")
        return username
