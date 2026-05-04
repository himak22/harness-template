#!/usr/bin/env python3
"""start.py — Inicia una sesión de trabajo sobre una feature.

Uso:
  ./harness/start.py              → Coge la siguiente pending de menor id
  ./harness/start.py <id>         → Coge la feature por id
  ./harness/start.py --role leader → Especifica rol (implementer por defecto)

El script:
  1. Valida que no haya ya una feature in_progress.
  2. Marca la feature como in_progress en feature_list.json.
  3. Inicializa progress/current.md con datos de la feature.
  4. Ejecuta security-check.py (si rules.security_checks es true).
  5. Ejecuta init.sh para validar el entorno.
  6. Muestra un resumen y mi rol.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# Determinar directorio base del proyecto (padre de harness/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
os.chdir(BASE_DIR)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def ok(msg): print(f"{GREEN}[OK]{NC}    {msg}")
def fail(msg): print(f"{RED}[FAIL]{NC}  {msg}")
def warn(msg): print(f"{YELLOW}[WARN]{NC}  {msg}")
def info(msg): print(f"{BLUE}[INFO]{NC}  {msg}")


def load_features():
    with open("feature_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_features(data):
    with open("feature_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def get_next_pending(features):
    pending = [f for f in features if f["status"] == "pending"]
    if not pending:
        return None
    return min(pending, key=lambda x: x["id"])


def get_feature_by_id(features, fid):
    for f in features:
        if f["id"] == fid:
            return f
    return None


def init_current_md(feature, role):
    template = f"""# Sesión actual

> Este archivo se vacía al cerrar cada sesión y se mueve a `history.md`.
> Mientras trabajas, **mantenlo actualizado en tiempo real**, no al final.

- **Feature en curso:** #{feature['id']} — {feature['name']}
- **Inicio:** {datetime.now().isoformat(timespec='minutes')}
- **Agente:** {role}

## Plan

1. Leer docs/architecture.md y docs/conventions.md.
2. Implementar según criterios de aceptación.
3. Escribir tests que cubran happy path + error path.
4. Ejecutar ./init.sh y asegurar que pasa.
5. Llamar a ./harness/done.sh para cerrar.

## Bitácora

_Anota aquí cada paso significativo: archivos creados, decisiones, bloqueos._

- [START] Sesión iniciada por {role}.

## Próximo paso

_Implementar la feature según acceptance criteria._
"""
    os.makedirs("progress", exist_ok=True)
    with open("progress/current.md", "w", encoding="utf-8") as f:
        f.write(template)


def main():
    parser = argparse.ArgumentParser(description="Inicia una sesión de trabajo")
    parser.add_argument("feature_id", nargs="?", type=int, help="ID de la feature (opcional)")
    parser.add_argument("--role", default="implementer", choices=["implementer", "leader", "reviewer"],
                        help="Rol del agente en esta sesión")
    args = parser.parse_args()

    print("═" * 58)
    print("  HARNESS START")
    print("═" * 58)

    # 1. Cargar features
    data = load_features()
    features = data.get("features", [])

    # 2. Verificar que no hay in_progress
    in_progress = [f for f in features if f["status"] == "in_progress"]
    if in_progress:
        f = in_progress[0]
        fail(f"Ya hay una sesión activa: #{f['id']} {f['name']}")
        print(f"  Ciérrala primero con: ./harness/done.sh (o ./harness/block.sh)")
        sys.exit(1)

    # 3. Elegir feature
    if args.feature_id:
        feature = get_feature_by_id(features, args.feature_id)
        if not feature:
            fail(f"No existe feature con id={args.feature_id}")
            sys.exit(1)
        if feature["status"] != "pending":
            fail(f"Feature #{feature['id']} no está en pending (está: {feature['status']})")
            sys.exit(1)
    else:
        feature = get_next_pending(features)
        if not feature:
            fail("No hay features pendientes.")
            sys.exit(1)

    # 4. Marcar in_progress
    feature["status"] = "in_progress"
    save_features(data)
    ok(f"Feature #{feature['id']} '{feature['name']}' → in_progress")

    # 5. Inicializar current.md
    init_current_md(feature, args.role)
    ok("progress/current.md inicializado")

    # 6. Ejecutar security-check (opcional, según feature_list.json)
    rules = data.get("rules", {})
    if rules.get("security_checks", True):
        print()
        print("── Verificando seguridad (security-check.py) ───────────")
        result = subprocess.run(["./harness/security-check.py"], capture_output=True, text=True)
        if result.returncode != 0:
            fail("Security check FALLÓ. Resuelve antes de continuar.")
            for line in result.stdout.splitlines():
                if "[FAIL]" in line:
                    print(f"  {line}")
            sys.exit(1)
        ok("Security check passed.")
    else:
        warn("Security checks desactivados en feature_list.json.")

    # 7. Ejecutar init.sh
    print()
    print("── Validando entorno (init.sh) ─────────────────────────")
    result = subprocess.run(["./init.sh"], capture_output=True, text=True)
    if result.returncode != 0:
        fail("init.sh FALLÓ. Resuelve antes de continuar.")
        for line in result.stdout.splitlines():
            if "[FAIL]" in line or "Error" in line:
                print(f"  {line}")
        sys.exit(1)
    ok("init.sh verde. Entorno listo.")

    # 8. Resumen + Decisión de subagentes
    print()
    print("═" * 58)
    info("DECISIÓN REQUERIDA: ¿Subagentes?")
    print()
    print("El agente DEBE comunicar al humano:")
    print(f"  'Feature #{feature['id']}. Complejidad: [baja/media/alta].")
    print(f"   Decisión: [directo / explorar+directo / subagentes].")
    print(f"   Razón: [criterio de docs/decision-framework.md].'")
    print()
    print("No tocar código hasta que el humano confirme.")
    print()
    info(f"ROL: {args.role}")
    print()
    print("═" * 58)
    info(f"ROL: {args.role}")
    if args.role == "leader":
        warn("NO edites src/ ni tests/. Orquesta subagentes.")
    elif args.role == "implementer":
        ok("Puedes editar src/ y tests/. Una sola feature.")
    elif args.role == "reviewer":
        warn("NO edites código. Valida y aprueba/rechaza.")
    print()
    info(f"Feature: #{feature['id']} {feature['name']}")
    print(f"  Title: {feature['title']}")
    print(f"  Desc:  {feature['description']}")
    print()
    print("Acceptance criteria:")
    for i, acc in enumerate(feature.get("acceptance", []), 1):
        print(f"  {i}. {acc}")
    print()
    print("═" * 58)


if __name__ == "__main__":
    main()
