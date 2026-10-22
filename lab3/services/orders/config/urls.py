from django.http import JsonResponse
from django.urls import include, path
from orders_app.views import ready
from orders_app.internal_views import customer_stats

urlpatterns = [
    path("api/", include("orders_app.urls")),
    path("internal/stats/customers/", customer_stats, name="customer-stats"),
    path("health/live/", lambda request: JsonResponse({"status": "ok"})),
    path("health/ready/", ready, name="ready"),
]
