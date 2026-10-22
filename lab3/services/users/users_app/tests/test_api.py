from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users_app.models import Customer


@override_settings(INTERNAL_API_KEY="test-internal-secret")
class UsersServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="Strongpass2026!")
        self.other = User.objects.create_user(username="bob", password="Strongpass2026!")
        self.admin = User.objects.create_superuser(username="admin", password="Strongpass2026!")
        self.c1 = Customer.objects.create(name="Alice", email="a@example.com", address="A", phone_number="1", user=self.user)
        self.c2 = Customer.objects.create(name="Bob", email="b@example.com", address="B", phone_number="2", user=self.other)

    def authorize(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return token.key

    def test_register_creates_user_customer_and_token(self):
        response = self.client.post("/api/register/", {
            "username": "newuser", "password": "Strongpass2026!",
            "password2": "Strongpass2026!", "first_name": "Алекс", "last_name": "Тест",
            "email": "new@example.com",
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Customer.objects.filter(user__username="newuser").exists())
        self.assertTrue(response.data.get("token"))

    def test_login_success_and_failure(self):
        self.assertEqual(self.client.post("/api/login/", {"username": "alice", "password": "Strongpass2026!"}).status_code, 200)
        self.assertEqual(self.client.post("/api/login/", {"username": "alice", "password": "incorrect"}).status_code, 401)

    def test_no_access_without_token(self):
        self.assertEqual(self.client.get("/api/customers/").status_code, 401)

    def test_regular_user_sees_only_own_customers(self):
        self.authorize(self.user)
        response = self.client.get("/api/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([x["id"] for x in response.data], [self.c1.id])
        self.assertEqual(self.client.get(f"/api/customers/{self.c2.id}/").status_code, 404)

    def test_user_cannot_assign_customer_to_someone_else(self):
        self.authorize(self.user)
        response = self.client.post("/api/customers/", {
            "name": "Another", "address": "A", "phone_number": "3",
            "email": "c@example.com", "user": self.other.id,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.get(pk=response.data["id"]).user_id, self.user.id)

    def test_admin_sees_everyone_and_can_filter(self):
        self.authorize(self.admin)
        self.assertEqual(len(self.client.get("/api/customers/").data), 2)
        filtered = self.client.get(f"/api/customers/?user_id={self.other.id}")
        self.assertEqual([x["id"] for x in filtered.data], [self.c2.id])
        self.assertEqual(len(self.client.get("/api/users/").data), 3)

    def test_regular_user_cannot_list_users(self):
        self.authorize(self.user)
        self.assertEqual(self.client.get("/api/users/").data, [])

    def test_internal_validation_rejects_missing_service_key(self):
        token = self.authorize(self.user)
        response = self.client.get("/internal/auth/validate/")
        self.assertEqual(response.status_code, 403)

    def test_internal_validation_returns_identity(self):
        token = self.authorize(self.user)
        response = self.client.get("/internal/auth/validate/", HTTP_X_SERVICE_KEY="test-internal-secret")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertFalse(response.data["is_superuser"])

    def test_internal_validation_rejects_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token badtoken")
        response = self.client.get("/internal/auth/validate/", HTTP_X_SERVICE_KEY="test-internal-secret")
        self.assertEqual(response.status_code, 401)

    @patch("users_app.views.requests.get")
    def test_customers_stats_reads_orders_service(self, get_mock):
        get_mock.return_value.status_code = 200
        get_mock.return_value.json.return_value = {"total_orders": 3, "customers_with_orders": 1}
        self.authorize(self.user)
        response = self.client.get("/api/customers/stats/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_count"], 1)
        self.assertEqual(response.data["total_orders"], 3)
        get_mock.assert_called_once()

    @patch("users_app.views.requests.get")
    def test_customers_stats_fails_cleanly_if_orders_unavailable(self, get_mock):
        import requests
        get_mock.side_effect = requests.ConnectionError("offline")
        self.authorize(self.user)
        self.assertEqual(self.client.get("/api/customers/stats/").status_code, 503)


@override_settings(INTERNAL_API_KEY="integration-test-secret")
class CustomerInternalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username="internal_owner", password="testPassword123!")
        self.customer = Customer.objects.create(name="Клиент", address="", phone_number="", email="x@example.com",
                                                user=self.owner)

    def test_customer_internal_requires_shared_key(self):
        self.assertEqual(self.client.get(f"/internal/customers/{self.customer.pk}/").status_code, 403)

    def test_customer_internal_blocks_foreign_user(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID=str(self.owner.pk + 10))
        self.assertEqual(self.client.get(f"/internal/customers/{self.customer.pk}/").status_code, 403)

    def test_customer_internal_returns_own_customer(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID=str(self.owner.pk))
        r = self.client.get(f"/internal/customers/{self.customer.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["user_id"], self.owner.pk)

    def test_customer_internal_allows_admin_service_request(self):
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret", HTTP_X_USER_ID="999",
                                HTTP_X_IS_SUPERUSER="true")
        self.assertEqual(self.client.get(f"/internal/customers/{self.customer.pk}/").status_code, 200)
