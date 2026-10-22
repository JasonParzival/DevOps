"""Развернуть ЛР3 на однонодном Docker Desktop Kubernetes (kubeadm).
Запуск из корня репозитория: python lab3/k8s/deploy.py
Безопасность: создаёт/меняет ТОЛЬКО ресурсы namespace lab3; PVC не удаляются.
"""
from __future__ import annotations

import json
import secrets
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NS = "lab3"
SERVICES = ("users", "catalog", "orders")


def run(*args: str, cwd: Path | None = None, capture: bool = False) -> str:
    cmd = [str(item) for item in args]
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(
        cmd, cwd=str(cwd or ROOT), check=True, text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return (result.stdout or "").strip()


def guard_context() -> None:
    context = run("kubectl", "config", "current-context", capture=True)
    if context != "docker-desktop":
        raise RuntimeError(
            f"Текущий Kubernetes context: {context!r}. Для безопасности запуск разрешён "
            "только в docker-desktop. Используй: kubectl config use-context docker-desktop"
        )
    info = json.loads(run("kubectl", "get", "nodes", "-o", "json", capture=True))
    nodes = info.get("items", [])
    if len(nodes) != 1:
        raise RuntimeError(f"Вместо однонодного кластера обнаружено нод: {len(nodes)}. "
                           "В Docker Desktop выбери kubeadm, одну ноду.")
    ready = any(c.get("type") == "Ready" and c.get("status") == "True"
                for c in nodes[0].get("status", {}).get("conditions", []))
    if not ready:
        raise RuntimeError("Единственная нода Kubernetes пока не Ready.")
    print("Проверка пройдена: docker-desktop, 1 нода, Ready.")


def build_images() -> None:
    for name in SERVICES:
        run("docker", "build", "-t", f"lab3-{name}:k8s-v1",
            str(ROOT / "lab3" / "services" / name))
    run("docker", "build", "-t", "lab3-frontend:k8s-v1",
        "-f", str(HERE.parent / "frontend" / "Dockerfile"), str(ROOT))
    print("Собраны 4 образа для Kubernetes (не заменяют образы из Compose).")


def ensure_secret_file() -> Path:
    file = HERE / ".secrets.generated.yaml"
    if file.exists():
        print("Существующий секрет Kubernetes сохранён: новые значения НЕ генерируются.")
        return file
    values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(40),
        "INTERNAL_API_KEY": secrets.token_urlsafe(40),
        "DJANGO_USERS_SECRET_KEY": secrets.token_urlsafe(48),
        "DJANGO_CATALOG_SECRET_KEY": secrets.token_urlsafe(48),
        "DJANGO_ORDERS_SECRET_KEY": secrets.token_urlsafe(48),
    }
    lines = [
        "# ЛОКАЛЬНЫЕ СЕКРЕТЫ. Не коммитить и никому не передавать.",
        "apiVersion: v1", "kind: Secret", "metadata:",
        "  name: lab3-secrets", "  namespace: lab3", "type: Opaque", "stringData:",
    ]
    lines.extend(f"  {key}: {value}" for key, value in values.items())
    file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        file.chmod(0o600)
    except OSError:
        pass
    print("Сгенерированы локальные секреты (значения не выводятся и в архив не входят).")
    return file


def kubectl_apply(filename: str | Path) -> None:
    run("kubectl", "apply", "-f", str(HERE / filename if isinstance(filename, str) else filename))


def wait_job(job: str, timeout: str = "240s") -> None:
    try:
        run("kubectl", "wait", "-n", NS, f"job/{job}",
            "--for=condition=complete", f"--timeout={timeout}")
    except subprocess.CalledProcessError:
        run("kubectl", "get", "pods", "-n", NS)
        run("kubectl", "logs", "-n", NS, f"job/{job}", "--tail=80")
        raise


def main() -> None:
    guard_context()
    build_images()
    kubectl_apply("00-namespace.yaml")
    kubectl_apply(ensure_secret_file())
    kubectl_apply("01-configmap.yaml")
    kubectl_apply("02-storage.yaml")
    kubectl_apply("03-postgres.yaml")
    run("kubectl", "rollout", "status", "statefulset/postgres", "-n", NS, "--timeout=300s")
    # Если задача запускается повторно, база сохраняется. Job пересоздаём, SQL идемпотентный.
    run("kubectl", "delete", "job", "lab3-init-databases", "-n", NS,
        "--ignore-not-found=true", "--wait=true")
    kubectl_apply("04-db-init.yaml")
    wait_job("lab3-init-databases")
    for name in SERVICES:
        job = f"lab3-migrate-{name}"
        run("kubectl", "delete", "job", job, "-n", NS,
            "--ignore-not-found=true", "--wait=true")
        kubectl_apply(f"05-migrate-{name}.yaml")
        wait_job(job)
    kubectl_apply("06-apps.yaml")
    for name in (*SERVICES, "frontend"):
        run("kubectl", "rollout", "status", f"deployment/{name}", "-n", NS, "--timeout=300s")
    run("kubectl", "get", "deploy,rs,pods,pvc,svc", "-n", NS)
    print("\nKubernetes развернут. В ДРУГОМ терминале запусти:")
    print("kubectl port-forward -n lab3 service/frontend 8086:80")
    print("Затем открой http://127.0.0.1:8086 и выполни:")
    print("set LAB3_GATEWAY_URL=http://127.0.0.1:8086    [CMD]")
    print("$env:LAB3_GATEWAY_URL='http://127.0.0.1:8086'    [PowerShell]")
    print("python lab3/scripts/smoke_test_nginx.py")


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, RuntimeError, FileNotFoundError, json.JSONDecodeError) as exc:
        print("\nОШИБКА: ", exc, file=sys.stderr)
        print("Проверь: kubectl get pods,pvc,jobs -n lab3", file=sys.stderr)
        print("И детали: kubectl describe pod <имя-pod> -n lab3", file=sys.stderr)
        sys.exit(1)
