import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db import connections
from rest_framework import generics, mixins, serializers, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import GenericViewSet
from .models import Customer
from .serializers import CustomerSerializer, RegisterSerializer, UserSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Customer.objects.create(
            name=f"{user.first_name} {user.last_name}".strip() or user.username,
            address="", phone_number="", email=user.email, user=user,
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
        if not user or not user.is_active:
            return Response({"error": "Неверное имя пользователя или пароль"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})


class UsersViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.all() if self.request.user.is_superuser else User.objects.none()


class CustomersViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Customer.objects.all()
        if self.request.user.is_superuser:
            owner_id = self.request.query_params.get("user_id")
            if owner_id:
                qs = qs.filter(user_id=owner_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = self.get_queryset()
        total_customers = qs.count()
        owner_id = None if request.user.is_superuser and not request.query_params.get("user_id") else (
            request.query_params.get("user_id") if request.user.is_superuser else str(request.user.pk)
        )
        params = {"user_id": owner_id} if owner_id else {}
        key = settings.INTERNAL_API_KEY
        if not key:
            return Response({"detail": "Не настроен ключ межсервисных запросов"}, status=503)
        try:
            response = requests.get(
                f"{settings.ORDERS_SERVICE_URL}/internal/stats/customers/",
                params=params, headers={"X-Service-Key": key}, timeout=3,
            )
            response.raise_for_status()
            metrics = response.json()
            total_orders = int(metrics["total_orders"])
            customers_with_orders = int(metrics["customers_with_orders"])
        except (requests.RequestException, ValueError, KeyError, TypeError):
            return Response({"detail": "Сервис заказов недоступен для статистики"}, status=503)
        return Response({
            "total_count": total_customers,
            "customers_with_orders": customers_with_orders,
            "total_orders": total_orders,
            "avg_orders_per_customer": round(total_orders / total_customers, 2) if total_customers else 0,
        })


@api_view(["GET"])
@permission_classes([AllowAny])
def ready(request):
    try:
        connections["default"].ensure_connection()
        return Response({"status": "ready"})
    except Exception:
        return Response({"status": "not_ready"}, status=503)
