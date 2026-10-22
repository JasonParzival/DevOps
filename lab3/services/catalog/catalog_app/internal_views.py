from secrets import compare_digest
from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Product

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def product_info(request, product_id):
    if not settings.INTERNAL_API_KEY or not compare_digest(
        request.headers.get("X-Service-Key", ""), settings.INTERNAL_API_KEY
    ):
        return Response({"detail": "Недоступно"}, status=403)
    requester = request.headers.get("X-User-ID", "")
    if not requester.isdecimal() or int(requester) < 1:
        return Response({"detail": "Некорректный пользователь"}, status=400)
    product = Product.objects.filter(pk=product_id).first()
    if not product:
        return Response({"detail": "Товар не найден"}, status=404)
    if request.headers.get("X-Is-Superuser", "false") != "true" and product.user_id != int(requester):
        return Response({"detail": "Нет доступа"}, status=403)
    return Response({
        "id": product.pk, "name": product.name, "price": str(product.price),
        "quantity": product.quantity, "user_id": product.user_id,
    })
