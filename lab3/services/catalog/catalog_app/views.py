from django.db import connections
from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class OwnedViewSet:
    """Users see their own rows; administrators may filter by user_id."""
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user_id")
            return qs.filter(user_id=user_id) if user_id else qs
        return qs.filter(user_id=self.request.user.pk)


class ProductsViewSet(OwnedViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            total_count=Count("id"), avg_price=Avg("price"),
            min_price=Min("price"), max_price=Max("price"),
            total_stock=Sum("quantity"),
        )
        return Response({
            "total_count": stats["total_count"],
            "avg_price": f'{stats["avg_price"]:.2f}' if stats["avg_price"] is not None else None,
            "min_price": f'{stats["min_price"]:.2f}' if stats["min_price"] is not None else None,
            "max_price": f'{stats["max_price"]:.2f}' if stats["max_price"] is not None else None,
            "total_stock": stats["total_stock"],
        })


class CategoriesViewSet(OwnedViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        categories = self.get_queryset()
        # Only products visible to this caller count toward the summary.
        products = Product.objects.all()
        if request.user.is_superuser:
            user_id = request.query_params.get("user_id")
            if user_id:
                products = products.filter(user_id=user_id)
        else:
            products = products.filter(user_id=request.user.pk)
        totals = categories.annotate(product_count=Count("product"))
        return Response({
            "total_count": categories.count(),
            "total_products": products.count(),
            "avg_products_per_category": round(totals.aggregate(avg=Avg("product_count"))["avg"] or 0, 2),
        })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ready(request):
    try:
        connections["default"].ensure_connection()
        return Response({"status": "ready"})
    except Exception:
        return Response({"status": "not_ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
