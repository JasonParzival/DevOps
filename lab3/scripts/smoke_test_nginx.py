"""Smoke-test the Vue entrypoint and all 3 microservices through Nginx on :8082.
Run from the repository root: python lab3/scripts/smoke_test_nginx.py
This creates a temporary user, product, customer and order in lab 3 databases.
"""
import os
from urllib.request import urlopen
import smoke_test

GATEWAY = os.getenv("LAB3_GATEWAY_URL", "http://127.0.0.1:8082").rstrip("/")


def main():
    with urlopen(GATEWAY + "/", timeout=10) as response:
        page = response.read()
        content_type = response.headers.get("Content-Type", "")
        assert response.status == 200, f"Frontend: HTTP {response.status}"
        assert "text/html" in content_type, f"Frontend: incorrect content type: {content_type}"
        assert b'id="app"' in page or b"id='app'" in page, "Vue mount point not found"
    print("Vue: главная страница через Nginx отвечает HTTP 200")

    with urlopen(GATEWAY + "/healthz", timeout=10) as response:
        assert response.status == 200, "Nginx health endpoint not ready"
    print("Nginx: /healthz отвечает HTTP 200")

    # Use the SAME API contracts tested on the individual service ports in stage 3.
    smoke_test.USER = GATEWAY
    smoke_test.CATALOG = GATEWAY
    smoke_test.ORDERS = GATEWAY
    smoke_test.main()
    print("УСПЕХ: frontend и все API микросервисы доступны через единый адрес", GATEWAY)


if __name__ == "__main__":
    main()
