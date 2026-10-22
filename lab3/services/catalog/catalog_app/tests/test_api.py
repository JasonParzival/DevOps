from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from catalog_app.models import Category, Product


@override_settings(INTERNAL_API_KEY="integration-test-secret")
class CatalogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_patch = patch("catalog_app.authentication.requests.get")
        self.auth_request = self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.mock_identity(1)
        self.alice_category = Category.objects.create(name="Milk", description="Dairy", user_id=1)
        self.bob_category = Category.objects.create(name="Bread", description="Bakery", user_id=2)
        self.alice_product = Product.objects.create(name="Молоко", price=Decimal("120.00"),
            description="1л", quantity=10, category=self.alice_category, user_id=1)
        self.bob_product = Product.objects.create(name="Хлеб", price=Decimal("50.00"),
            description="Булка", quantity=7, category=self.bob_category, user_id=2)

    def mock_identity(self, user_id, superuser=False):
        self.auth_request.return_value.status_code = 200
        self.auth_request.return_value.json.return_value = {
            "id": user_id, "username": f"user{user_id}", "is_active": True,
            "is_staff": superuser, "is_superuser": superuser,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token example-token")

    def test_unauthenticated_requires_token(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/products/").status_code, 401)

    def test_regular_user_sees_only_own_products_and_categories(self):
        resp = self.client.get("/api/products/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([item["id"] for item in resp.data], [self.alice_product.pk])
        resp = self.client.get("/api/categories/")
        self.assertEqual([item["id"] for item in resp.data], [self.alice_category.pk])
        self.assertEqual(self.client.get(f"/api/products/{self.bob_product.pk}/").status_code, 404)

    def test_new_category_uses_authenticated_identity_not_user_payload(self):
        resp = self.client.post("/api/categories/", {
            "name": "Drinks", "description": "Water", "user": 200,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["user"], 1)
        self.assertEqual(Category.objects.get(pk=resp.data["id"]).user_id, 1)

    def test_new_product_uses_category_and_preserves_api_shape(self):
        resp = self.client.post("/api/products/", {
            "name": "Масло", "description": "Сливочное", "price": "200.40",
            "quantity": 5, "category": self.alice_category.pk, "user": 200,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["user"], 1)
        self.assertEqual(resp.data["category"], self.alice_category.pk)
        self.assertEqual(resp.data["price"], "200.40")

    def test_cannot_attach_other_users_category(self):
        resp = self.client.post("/api/products/", {
            "name": "Чужой", "description": "Bad", "price": "2.00",
            "quantity": 3, "category": self.bob_category.pk,
        })
        self.assertEqual(resp.status_code, 400)

    def test_admin_can_filter_products_and_categories(self):
        self.mock_identity(3, superuser=True)
        self.assertEqual(len(self.client.get("/api/products/").data), 2)
        self.assertEqual([x["id"] for x in self.client.get("/api/products/?user_id=2").data], [self.bob_product.pk])
        self.assertEqual([x["id"] for x in self.client.get("/api/categories/?user_id=1").data], [self.alice_category.pk])

    def test_update_and_delete_owned_product(self):
        resp = self.client.patch(f"/api/products/{self.alice_product.pk}/", {"quantity": 8})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["quantity"], 8)
        self.assertEqual(self.client.delete(f"/api/products/{self.alice_product.pk}/").status_code, 204)

    def test_product_stats_match_vue_schema(self):
        data = self.client.get("/api/products/stats/").data
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["total_stock"], 10)
        self.assertEqual(data["avg_price"], "120.00")
        self.assertEqual(data["min_price"], "120.00")
        self.assertEqual(data["max_price"], "120.00")

    def test_categories_stats_match_vue_schema(self):
        data = self.client.get("/api/categories/stats/").data
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["total_products"], 1)
        self.assertEqual(data["avg_products_per_category"], 1.0)

    def test_wrong_token_rejected(self):
        self.auth_request.return_value.status_code = 401
        self.assertEqual(self.client.get("/api/products/").status_code, 401)

    def test_users_service_unavailable_returns_503(self):
        import requests
        self.auth_request.side_effect = requests.ConnectionError("offline")
        self.assertEqual(self.client.get("/api/products/").status_code, 503)

    def test_missing_service_key_returns_503(self):
        with override_settings(INTERNAL_API_KEY=""):
            self.assertEqual(self.client.get("/api/products/").status_code, 503)

    def test_inactive_user_rejected(self):
        self.auth_request.return_value.json.return_value["is_active"] = False
        self.assertEqual(self.client.get("/api/products/").status_code, 401)

    def test_request_passes_token_and_shared_key_to_users_service(self):
        self.client.get("/api/products/")
        _, kwargs = self.auth_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Token example-token")
        self.assertEqual(kwargs["headers"]["X-Service-Key"], "integration-test-secret")
        self.assertEqual(kwargs["timeout"], 3)

    def test_health_probes_are_public(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/health/live/").status_code, 200)
        self.assertEqual(self.client.get("/health/ready/").status_code, 200)


@override_settings(INTERNAL_API_KEY="integration-test-secret")
class CatalogInternalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Товары", description="Основная", user_id=4)
        self.product = Product.objects.create(name="Чай", price="80.00", description="Черный", quantity=9,
                                              category=self.category, user_id=4)

    def test_internal_product_requires_shared_key(self):
        self.assertEqual(self.client.get(f"/internal/products/{self.product.pk}/").status_code, 403)

    def test_internal_product_rejects_foreign_user(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID="5")
        self.assertEqual(self.client.get(f"/internal/products/{self.product.pk}/").status_code, 403)

    def test_internal_product_returns_snapshot(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID="4")
        r = self.client.get(f"/internal/products/{self.product.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["price"], "80.00")
        self.assertEqual(r.data["quantity"], 9)

    def test_internal_admin_can_validate_product(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID="1",
                                HTTP_X_IS_SUPERUSER="true")
        self.assertEqual(self.client.get(f"/internal/products/{self.product.pk}/").status_code, 200)
