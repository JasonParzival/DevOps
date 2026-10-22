from secrets import compare_digest
from django.conf import settings
from django.db.models import Count
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Order


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def customer_stats(request):
    key = request.headers.get("X-Service-Key", "")
    if not settings.INTERNAL_API_KEY or not compare_digest(key, settings.INTERNAL_API_KEY):
        return Response({"detail": "Недоступно"}, status=403)
    qs = Order.objects.all()
    owner = request.query_params.get("user_id")
    if owner:
        if not owner.isdecimal() or int(owner) < 1:
            return Response({"detail": "Invalid user_id"}, status=400)
        qs = qs.filter(user_id=int(owner))
    return Response({
        "total_orders": qs.count(),
        "customers_with_orders": qs.values("customer_id").distinct().count(),
    })
