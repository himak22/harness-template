#!/usr/bin/env python3
"""done.py — Cierra una sesión de trabajo marcando la feature como done.

Uso: ./harness/done.py

El script:
  1. Ejecuta security-check.py (si rules.security_checks es true en feature_list.json).
  2. Ejecuta init.sh. Si falla, ABORTA (no se puede cerrar sin tests verdes).
  3. Marca la feature in_progress como done en feature_list.json.
  4. Mueve progress/current.md a progress/history.md (append).
  5. Vacía progress/current.md con la plantilla limpia.
"""

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


def _validate_not_symlink(path):
    """Abort if path is a symlink to prevent TOCTOU attacks."""
    if os.path.islink(path):
        fail(f"Security violation: {path} is a symlink. Aborting.")
        sys.exit(1)


def load_features():
    _validate_not_symlink("feature_list.json")
    with open("feature_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_features(data):
    _validate_not_symlink("feature_list.json")
    with open("feature_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    print("═" * 58)
    print("  HARNESS DONE")
    print("═" * 58)

    # 1. Cargar features
    data = load_features()
    features = data.get("features", [])

    in_progress = [f for f in features if f["status"] == "in_progress"]
    if not in_progress:
        fail("No hay ninguna feature in_progress. Nada que cerrar.")
        sys.exit(1)

    feature = in_progress[0]

    # 2. Ejecutar security-check (opcional, según feature_list.json)
    rules = data.get("rules", {})
    if rules.get("security_checks", True):
        print("── Paso 1: Ejecutando security-check.py ────────────────")
        result = subprocess.run(["./harness/security-check.py"], capture_output=True, text=True)
        if result.returncode != 0:
            fail("Security check FALLÓ. No se puede cerrar la sesión.")
            print()
            print("Errores:")
            for line in result.stdout.splitlines():
                if "[FAIL]" in line:
                    print(f"  {line}")
            print()
            warn("Corrige los problemas de seguridad y vuelve a ejecutar ./harness/done.py")
            sys.exit(1)
        ok("Security check passed.")
    else:
        warn("Security checks desactivados en feature_list.json. Saltando.")

    # 3. Ejecutar init.sh (OBLIGATORIO)
    print()
    print("── Paso 2: Ejecutando init.sh ──────────────────────────")
    result = subprocess.run(["./init.sh"], capture_output=True, text=True)
    if result.returncode != 0:
        fail("init.sh FALLÓ. No se puede cerrar la sesión.")
        print()
        print("Errores:")
        for line in result.stdout.splitlines():
            if "[FAIL]" in line or "Error" in line:
                print(f"  {line}")
        print()
        warn("Corrige los errores y vuelve a ejecutar ./harness/done.py")
        sys.exit(1)
    ok("init.sh verde. Tests pasan.")

    # 4. Marcar como done
    print()
    print("── Paso 3: Marcando feature como done ──────────────────")
    feature["status"] = "done"
    save_features(data)
    ok(f"Feature #{feature['id']} '{feature['name']}' → done")

    # 5. Archivar current.md en history.md
    print()
    print("── Paso 4: Archivando sesión ───────────────────────────")
    if not os.path.exists("progress/current.md"):
        warn("No existe progress/current.md")
    else:
        _validate_not_symlink("progress/current.md")
        with open("progress/current.md", "r", encoding="utf-8") as f:
            current_content = f.read()

        # Prepend session header
        archive_entry = f"""
---

## {datetime.now().strftime('%Y-%m-%d')} — Feature {feature['id']}: {feature['name']}
- **Agente:** (ver progress/current.md)
- **Resultado:** done

{current_content}
"""
        _validate_not_symlink("progress/history.md")
        with open("progress/history.md", "a", encoding="utf-8") as f:
            f.write(archive_entry)
        ok("Sesión archivada en progress/history.md")

    # 6. Vaciar current.md
    _validate_not_symlink("progress/current.md")
    template = """# Sesión actual

> Este archivo se vacía al cerrar cada sesión y se mueve a `history.md`.
> Mientras trabajas, **mantenlo actualizado en tiempo real**, no al final.

- **Feature en curso:** _ninguna_
- **Inicio:** _—_
- **Agente:** _—_

## Plan

_Describe en 3-5 bullets qué vas a hacer antes de tocar código._

## Bitácora

_Anota aquí cada paso significativo: archivos creados, decisiones, bloqueos._

- ...

## Próximo paso

_Si la sesión se interrumpe, lo primero que debe hacer la siguiente sesión._
"""
    with open("progress/current.md", "w", encoding="utf-8") as f:
        f.write(template)
    ok("progress/current.md vaciado")

    print()
    print("═" * 58)
    ok("Sesión cerrada correctamente.")
    info(f"Feature #{feature['id']} completada.")
    print("═" * 58)


if __name__ == "__main__":
    main()
