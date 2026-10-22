from datetime import date
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from orders_app.models import Order, OrderDetail
from orders_app.authentication import RemoteUser


@override_settings(INTERNAL_API_KEY="integration-test-secret")
class OrdersTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resource_patch = patch("orders_app.services.requests.get")
        self.resource_request = self.resource_patch.start()
        self.addCleanup(self.resource_patch.stop)
        self.auth_as(1)
        self.resource_request.return_value.status_code = 200
        self.resource_request.return_value.json.return_value = {
            "id": 8, "quantity": 10, "name": "Молоко", "price": "120.00", "user_id": 1,
        }
        self.alice = Order.objects.create(order_number=1, date=date(2026, 10, 15),
            status="В обработке", customer_id=8, user_id=1)
        self.bob = Order.objects.create(order_number=2, date=date(2026, 10, 15),
            status="В сборке", customer_id=9, user_id=2)

    def auth_as(self, user_id, superuser=False):
        user = RemoteUser(id=user_id, username=f"user{user_id}", is_active=True,
                          is_staff=superuser, is_superuser=superuser)
        self.client.force_authenticate(user=user, token="sample-token")

    def test_anonymous_cannot_read_orders(self):
        self.client = APIClient()
        self.client.credentials()
        self.assertEqual(self.client.get("/api/orders/").status_code, 401)

    def test_user_sees_only_own_orders(self):
        r = self.client.get("/api/orders/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([x["id"] for x in r.data], [self.alice.pk])
        self.assertEqual(self.client.get(f"/api/orders/{self.bob.pk}/").status_code, 404)

    def test_admin_can_filter_orders(self):
        self.auth_as(3, True)
        self.assertEqual(len(self.client.get("/api/orders/").data), 2)
        self.assertEqual(len(self.client.get("/api/orders/?user_id=2").data), 1)

    def test_create_order_checks_customer_and_owner(self):
        r = self.client.post("/api/orders/", {
            "order_number": 3, "date": "2026-10-15", "status": "В обработке",
            "customer": 8, "user": 999,
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["customer"], 8)
        self.assertEqual(r.data["user"], 1)
        self.assertTrue(self.resource_request.called)

    def test_create_order_rejects_missing_customer(self):
        self.resource_request.return_value.status_code = 404
        r = self.client.post("/api/orders/", {"order_number": 4, "date": "2026-10-15", "customer": 8})
        self.assertEqual(r.status_code, 400)

    def test_upstream_unavailable_is_not_created(self):
        import requests
        self.resource_request.side_effect = requests.ConnectionError("offline")
        r = self.client.post("/api/orders/", {"order_number": 4, "date": "2026-10-15", "customer": 8})
        self.assertEqual(r.status_code, 503)

    def test_order_status_update(self):
        r = self.client.patch(f"/api/orders/{self.alice.pk}/", {"status": "В сборке"})
        self.assertEqual(r.status_code, 200)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.status, "В сборке")

    def test_create_detail_checks_catalog_and_snapshots_price(self):
        r = self.client.post("/api/orderDetails/", {"order": self.alice.pk, "product": 8, "quantity": 2})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["user"], 1)
        self.assertEqual(r.data["product"], 8)
        self.assertEqual(r.data["product_price"], "120.00")
        self.assertEqual(r.data["product_name"], "Молоко")

    def test_cannot_add_to_foreign_order(self):
        r = self.client.post("/api/orderDetails/", {"order": self.bob.pk, "product": 8, "quantity": 2})
        self.assertEqual(r.status_code, 400)

    def test_cannot_exceed_stock(self):
        r = self.client.post("/api/orderDetails/", {"order": self.alice.pk, "product": 8, "quantity": 500})
        self.assertEqual(r.status_code, 400)

    def test_cannot_use_missing_product(self):
        self.resource_request.return_value.status_code = 404
        r = self.client.post("/api/orderDetails/", {"order": self.alice.pk, "product": 8, "quantity": 2})
        self.assertEqual(r.status_code, 400)

    def test_user_detail_scope(self):
        OrderDetail.objects.create(order=self.alice, product_id=8, quantity=1, user_id=1, product_price="120.00")
        OrderDetail.objects.create(order=self.bob, product_id=9, quantity=1, user_id=2, product_price="20.00")
        self.assertEqual(len(self.client.get("/api/orderDetails/").data), 1)

    def test_delete_order_cascades_details(self):
        OrderDetail.objects.create(order=self.alice, product_id=8, quantity=1, user_id=1)
        self.assertEqual(self.client.delete(f"/api/orders/{self.alice.pk}/").status_code, 204)
        self.assertFalse(OrderDetail.objects.exists())

    def test_orders_stats_shape(self):
        r = self.client.get("/api/orders/stats/")
        self.assertEqual(set(r.data), {"total_count", "orders_today", "orders_this_month", "status_distribution"})
        self.assertEqual(r.data["total_count"], 1)

    def test_details_stats_shape(self):
        OrderDetail.objects.create(order=self.alice, product_id=8, quantity=3, user_id=1)
        r = self.client.get("/api/orderDetails/stats/")
        self.assertEqual(r.data["total_count"], 1)
        self.assertEqual(r.data["total_quantity"], 3)

    def test_internal_customer_stats_requires_key(self):
        self.client = APIClient()
        self.client.credentials()
        self.assertEqual(self.client.get("/internal/stats/customers/").status_code, 403)

    def test_internal_customer_stats_owner_filter(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_SERVICE_KEY="integration-test-secret")
        r = self.client.get("/internal/stats/customers/?user_id=1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, {"total_orders": 1, "customers_with_orders": 1})

    def test_health_probes(self):
        self.client = APIClient()
        self.client.credentials()
        self.assertEqual(self.client.get("/health/live/").status_code, 200)
        self.assertEqual(self.client.get("/health/ready/").status_code, 200)
