from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomersViewSet, UsersViewSet

router = DefaultRouter()
router.register("users", UsersViewSet, basename="user")
router.register("customers", CustomersViewSet, basename="customer")

urlpatterns = [path("", include(router.urls))]
