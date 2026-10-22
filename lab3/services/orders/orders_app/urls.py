from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import OrdersViewSet, OrderDetailsViewSet

router = DefaultRouter()
router.register("orders", OrdersViewSet, basename="order")
router.register("orderDetails", OrderDetailsViewSet, basename="orderDetail")
urlpatterns = [path("", include(router.urls))]
