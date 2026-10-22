from django.db import connections
from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .models import Order, OrderDetail, STATUS_CHOICES
from .serializers import OrderSerializer, OrderDetailSerializer


class OwnedViewSet:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user_id")
            return qs.filter(user_id=user_id) if user_id else qs
        return qs.filter(user_id=self.request.user.pk)


class OrdersViewSet(OwnedViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = self.get_queryset()
        today = timezone.localdate()
        distribution = {label: qs.filter(status=value).count() for value, label in STATUS_CHOICES}
        return Response({
            "total_count": qs.count(),
            "orders_today": qs.filter(date=today).count(),
            "orders_this_month": qs.filter(date__year=today.year, date__month=today.month).count(),
            "status_distribution": distribution,
        })


class OrderDetailsViewSet(OwnedViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin, GenericViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        metrics = self.get_queryset().aggregate(
            total_count=Count("id"), total_quantity=Sum("quantity"),
            avg_quantity=Avg("quantity"), min_quantity=Min("quantity"),
            max_quantity=Max("quantity"),
        )
        return Response(metrics)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ready(request):
    try:
        connections["default"].ensure_connection()
        return Response({"status": "ready"})
    except Exception:
        return Response({"status": "not_ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
