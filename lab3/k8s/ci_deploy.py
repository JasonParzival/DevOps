"""Jenkins-деплой ЛР3 на существующий Docker Desktop Kubernetes.

Не создаёт/не пересоздаёт Kubernetes Secret и PostgreSQL. Не удаляет PVC.
Предполагает: первичный деплой уже выполнен через lab3/k8s/deploy.py.

Использование:
    python lab3/k8s/ci_deploy.py --check-only
    python lab3/k8s/ci_deploy.py --tag k8s-j42
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from deploy import guard_context

HERE = Path(__file__).resolve().parent
NS = "lab3"
APPS = ("users", "catalog", "orders", "frontend")
BACKENDS = ("users", "catalog", "orders")
TAG_PATTERN = re.compile(r"k8s-j[1-9][0-9]*\Z")


def command(*args: str, input_yaml: str | None = None, capture: bool = False) -> str:
    args_list = [str(part) for part in args]
    print("+", " ".join(args_list), flush=True)
    completed = subprocess.run(
        args_list,
        input=input_yaml,
        text=True,
        check=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return (completed.stdout or "").strip()


def check_preconditions() -> None:
    guard_context()
    command("kubectl", "get", "namespace", NS, "-o", "name")
    # Важно: уже созданный секрет читаем только по имени, но не выводим содержимое.
    command("kubectl", "get", "secret", "lab3-secrets", "-n", NS, "-o", "name")
    command("kubectl", "get", "statefulset", "postgres", "-n", NS, "-o", "name")
    for claim in ("postgres-data", "users-media", "catalog-media"):
        command("kubectl", "get", "pvc", claim, "-n", NS, "-o", "name")
    print("Проверено: Docker Desktop kubeadm, namespace, Secret, PostgreSQL и PVC существуют.")


def replace_image(manifest: str, name: str, tag: str) -> str:
    old = f"image: lab3-{name}:k8s-v1"
    new = f"image: lab3-{name}:{tag}"
    if manifest.count(old) != 1:
        raise RuntimeError(f"Ожидали одно вхождение {old!r} в Kubernetes YAML.")
    return manifest.replace(old, new)


def render_job(name: str, tag: str) -> str:
    yaml_text = (HERE / f"05-migrate-{name}.yaml").read_text(encoding="utf-8")
    return replace_image(yaml_text, name, tag)


def render_apps(tag: str) -> str:
    yaml_text = (HERE / "06-apps.yaml").read_text(encoding="utf-8")
    # Проверка защищает уже исправленные health probes от случайного отката к HTTP 400.
    if yaml_text.count("name: Host") < 6 or yaml_text.count("value: localhost") < 6:
        raise RuntimeError("В 06-apps.yaml отсутствует исправление Host: localhost в шести Django probes.")
    for name in APPS:
        yaml_text = replace_image(yaml_text, name, tag)
    return yaml_text


def assert_images(tag: str) -> None:
    for name in APPS:
        command("docker", "image", "inspect", f"lab3-{name}:{tag}", "--format", "{{.Id}}")


def migrate(name: str, tag: str) -> None:
    job = f"lab3-migrate-{name}"
    yaml_text = render_job(name, tag)
    command("kubectl", "delete", "job", job, "-n", NS,
            "--ignore-not-found=true", "--wait=true")
    command("kubectl", "apply", "-f", "-", input_yaml=yaml_text)
    try:
        command("kubectl", "wait", "-n", NS, f"job/{job}",
                "--for=condition=complete", "--timeout=240s")
    except subprocess.CalledProcessError:
        # Выводим диагностические сведения без значений секретов.
        subprocess.run(["kubectl", "logs", "-n", NS, f"job/{job}", "--tail=80"], check=False)
        raise


def deploy(tag: str) -> None:
    # Теги уникальны для каждой Jenkins-сборки. Это вызывает настоящий rolling update,
    # в отличие от повторного применения исходного k8s-v1 без изменения Pod template.
    assert_images(tag)
    apps_yaml = render_apps(tag)
    command("kubectl", "rollout", "status", "statefulset/postgres", "-n", NS, "--timeout=180s")
    # Миграции до обновления приложения (только обратно совместимые изменения схемы).
    for name in BACKENDS:
        migrate(name, tag)
    command("kubectl", "apply", "-f", "-", input_yaml=apps_yaml)
    for name in APPS:
        command("kubectl", "rollout", "status", f"deployment/{name}",
                "-n", NS, "--timeout=300s")
    command("kubectl", "get", "deploy,rs,pods", "-n", NS)
    print(f"Развёртывание {tag} успешно. PVC и действующий Kubernetes Secret сохранены.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--tag", help="Уникальный тег Jenkins, например k8s-j42")
    args = parser.parse_args()
    if not args.check_only and (not args.tag or not TAG_PATTERN.fullmatch(args.tag)):
        parser.error("Для деплоя укажи --tag k8s-j<положительное число>.")
    check_preconditions()
    if args.check_only:
        print("Проверка окружения завершена. Изменений не было.")
        return
    deploy(args.tag)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(f"Ошибка CI/CD: {error}", file=sys.stderr)
        print("Проверь доступ Jenkins к Docker Desktop и kubectl context docker-desktop.", file=sys.stderr)
        sys.exit(1)
