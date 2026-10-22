from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from users_app.internal_views import validate_token
from users_app.customer_internal import customer_info
from users_app.views import RegisterView, LoginView, ready

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users_app.urls")),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("internal/auth/validate/", validate_token, name="validate-token"),
    path("internal/customers/<int:customer_id>/", customer_info, name="internal-customer"),
    path("health/live/", lambda request: JsonResponse({"status": "ok"})),
    path("health/ready/", ready, name="ready"),
]
