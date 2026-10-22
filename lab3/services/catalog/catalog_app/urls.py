from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoriesViewSet, ProductsViewSet

router = DefaultRouter()
router.register("products", ProductsViewSet, basename="product")
router.register("categories", CategoriesViewSet, basename="category")
urlpatterns = [path("", include(router.urls))]
