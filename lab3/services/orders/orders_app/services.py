"""Inter-service calls. Public clients cannot reach these internal routes via Nginx."""
import requests
from django.conf import settings
from rest_framework.exceptions import APIException, ValidationError

class UpstreamUnavailable(APIException):
    status_code = 503
    default_detail = "Зависимый микросервис временно недоступен"


def get_owned_resource(url, requester, field_name):
    if not settings.INTERNAL_API_KEY:
        raise UpstreamUnavailable("Отсутствует ключ межсервисного взаимодействия")
    try:
        response = requests.get(url, headers={
            "X-Service-Key": settings.INTERNAL_API_KEY,
            "X-User-ID": str(requester.pk),
            "X-Is-Superuser": "true" if requester.is_superuser else "false",
        }, timeout=3)
    except requests.RequestException as exc:
        raise UpstreamUnavailable() from exc
    if response.status_code in (403, 404):
        raise ValidationError({field_name: "Объект не найден или недоступен пользователю"})
    if response.status_code != 200:
        raise UpstreamUnavailable()
    try:
        data = response.json()
        if not isinstance(data, dict) or int(data["id"]) <= 0:
            raise ValueError("Malformed upstream response")
        return data
    except (ValueError, TypeError, KeyError) as exc:
        raise UpstreamUnavailable() from exc


def customer_info(requester, customer_id):
    return get_owned_resource(
        f"{settings.USERS_SERVICE_URL}/internal/customers/{customer_id}/",
        requester, "customer")


def product_info(requester, product_id):
    return get_owned_resource(
        f"{settings.CATALOG_SERVICE_URL}/internal/products/{product_id}/",
        requester, "product")
