from secrets import compare_digest
from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Customer

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def customer_info(request, customer_id):
    if not settings.INTERNAL_API_KEY or not compare_digest(
        request.headers.get("X-Service-Key", ""), settings.INTERNAL_API_KEY
    ):
        return Response({"detail": "Недоступно"}, status=403)
    requester = request.headers.get("X-User-ID", "")
    if not requester.isdecimal() or int(requester) < 1:
        return Response({"detail": "Некорректный пользователь"}, status=400)
    customer = Customer.objects.filter(pk=customer_id).first()
    if not customer:
        return Response({"detail": "Клиент не найден"}, status=404)
    if request.headers.get("X-Is-Superuser", "false") != "true" and customer.user_id != int(requester):
        return Response({"detail": "Нет доступа"}, status=403)
    return Response({"id": customer.pk, "user_id": customer.user_id, "name": customer.name})
