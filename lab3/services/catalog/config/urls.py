from django.http import JsonResponse
from django.urls import include, path
from catalog_app.views import ready
from catalog_app.internal_views import product_info

urlpatterns = [
    path("api/", include("catalog_app.urls")),
    path("internal/products/<int:product_id>/", product_info, name="internal-product"),
    path("health/live/", lambda request: JsonResponse({"status": "ok"})),
    path("health/ready/", ready, name="ready"),
]
