"""Real HTTP smoke check for users -> catalog -> orders. Requires running Compose services."""
import json
import secrets
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER = "http://127.0.0.1:8003"
CATALOG = "http://127.0.0.1:8004"
ORDERS = "http://127.0.0.1:8005"


def api(base, method, path, payload=None, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Token " + token
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(base + path, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=8) as response:
            return json.load(response)
    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {base}{path} -> HTTP {error.code}: {message[:600]}") from error
    except URLError as error:
        raise RuntimeError(f"{method} {base}{path} -> connection error: {error}") from error


def main():
    suffix = secrets.token_hex(5)
    username = "lab3_smoke_" + suffix
    password = "Strongpass_2026!" + suffix
    registered = api(USER, "POST", "/api/register/", {
        "username": username, "password": password, "password2": password,
        "email": f"{username}@example.test", "first_name": "Тест", "last_name": "ЛР3",
    })
    token = registered["token"]
    print("1/7 users: регистрация и DRF-токен получены")

    customers = api(USER, "GET", "/api/customers/", token=token)
    customer = next(row for row in customers if row["user"] == registered["user"]["id"])
    print("2/7 users: собственный Customer найден, ID", customer["id"])

    category = api(CATALOG, "POST", "/api/categories/", {
        "name": "ЛР3 " + suffix, "description": "Проверка микросервисов"}, token)
    print("3/7 catalog: категория создана, ID", category["id"])

    product = api(CATALOG, "POST", "/api/products/", {
        "name": "Проверочный товар " + suffix, "price": "125.50", "description": "HTTP интеграция",
        "quantity": 10, "category": category["id"]}, token)
    print("4/7 catalog: товар создан, ID", product["id"])

    order = api(ORDERS, "POST", "/api/orders/", {
        "order_number": 1, "date": date.today().isoformat(),
        "status": "В обработке", "customer": customer["id"]}, token)
    print("5/7 orders: заказ создан, ID", order["id"])

    detail = api(ORDERS, "POST", "/api/orderDetails/", {
        "order": order["id"], "product": product["id"], "quantity": 2}, token)
    assert detail["product_price"] == "125.50", detail
    print("6/7 orders: позиция добавлена, цена сохранена", detail["product_price"])

    stats = api(USER, "GET", "/api/customers/stats/", token=token)
    assert stats["total_orders"] == 1, stats
    assert stats["customers_with_orders"] == 1, stats
    print("7/7 users -> orders: статистика клиента корректна")
    print("УСПЕХ: HTTP-интеграция трех микросервисов подтверждена")
    print("Тестовый пользователь:", username, "(токен и пароль не выводятся)")


if __name__ == "__main__":
    main()
