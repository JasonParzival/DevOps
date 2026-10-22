"""Validate the existing DRF Token header with users-service; do not copy users."""
from dataclasses import dataclass
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException, AuthenticationFailed


class AuthenticationServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Сервис авторизации временно недоступен"
    default_code = "auth_unavailable"


@dataclass(frozen=True)
class RemoteUser:
    id: int
    username: str
    is_active: bool
    is_staff: bool
    is_superuser: bool

    @property
    def pk(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username


class RemoteTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        value = request.headers.get("Authorization", "")
        if not value:
            return None
        parts = value.split()
        if len(parts) != 2 or parts[0].lower() != "token":
            raise AuthenticationFailed("Ожидается заголовок Authorization: Token <token>")
        if not settings.INTERNAL_API_KEY:
            raise AuthenticationServiceUnavailable()
        try:
            response = requests.get(
                f"{settings.USERS_SERVICE_URL}/internal/auth/validate/",
                headers={"Authorization": f"Token {parts[1]}",
                         "X-Service-Key": settings.INTERNAL_API_KEY},
                timeout=3,
            )
            if response.status_code == 401:
                raise AuthenticationFailed("Недействительный токен")
            if response.status_code != 200:
                raise AuthenticationServiceUnavailable()
            identity = response.json()
            # Exact shape is controlled by users-service, never the client.
            user = RemoteUser(
                id=int(identity["id"]), username=str(identity["username"]),
                is_active=identity["is_active"], is_staff=identity["is_staff"],
                is_superuser=identity["is_superuser"],
            )
            if user.id <= 0 or not all(isinstance(v, bool) for v in
                                      (user.is_active, user.is_staff, user.is_superuser)):
                raise ValueError("Malformed identity")
            if not user.is_active:
                raise AuthenticationFailed("Учётная запись отключена")
            return (user, parts[1])
        except (requests.RequestException, KeyError, ValueError, TypeError):
            raise AuthenticationServiceUnavailable()

    def authenticate_header(self, request):
        return "Token"
