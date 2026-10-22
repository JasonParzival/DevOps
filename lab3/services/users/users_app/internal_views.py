from secrets import compare_digest
from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def validate_token(request):
    expected_key = settings.INTERNAL_API_KEY
    supplied_key = request.headers.get("X-Service-Key", "")
    if not expected_key or not compare_digest(supplied_key, expected_key):
        return Response({"detail": "Недоступно"}, status=status.HTTP_403_FORBIDDEN)

    # Authenticating explicitly keeps the endpoint inaccessible to public requests
    # even though it must not trigger default authentication before service-key check.
    authenticator = TokenAuthentication()
    try:
        result = authenticator.authenticate(request)
    except AuthenticationFailed:
        return Response({"detail": "Недействительный токен"}, status=status.HTTP_401_UNAUTHORIZED)
    if result is None:
        return Response({"detail": "Требуется токен"}, status=status.HTTP_401_UNAUTHORIZED)
    user, _token = result
    return Response({
        "id": user.pk, "username": user.username, "is_active": user.is_active,
        "is_staff": user.is_staff, "is_superuser": user.is_superuser,
    })
