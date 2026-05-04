#!/usr/bin/env python3
"""doctor.py — Repara inconsistencias en el estado del arnés.

Uso: ./harness/doctor.py

Detecta y repara problemas comunes:
  - Feature done pero current.md no vacío
  - current.md dice "ninguna" pero hay in_progress en feature_list
  - Más de un in_progress en feature_list
  - current.md vacío pero hay in_progress (sin bitácora)
"""

import json
import os
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


def ok(msg): print(f"{GREEN}[FIXED]{NC}  {msg}")
def warn(msg): print(f"{YELLOW}[WARN]{NC}  {msg}")
def info(msg): print(f"{BLUE}[INFO]{NC}  {msg}")


def load_features():
    with open("feature_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_features(data):
    with open("feature_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_current_md():
    if not os.path.exists("progress/current.md"):
        return ""
    with open("progress/current.md", "r", encoding="utf-8") as f:
        return f.read()


def is_current_md_empty(content):
    return "Feature en curso: _ninguna_" in content or "Feature en curso: _—_" in content


def empty_current_md():
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
    os.makedirs("progress", exist_ok=True)
    with open("progress/current.md", "w", encoding="utf-8") as f:
        f.write(template)


def archive_current_md(feature_name, result="repaired by doctor"):
    if not os.path.exists("progress/current.md"):
        return
    with open("progress/current.md", "r", encoding="utf-8") as f:
        content = f.read()

    archive_entry = f"""
---

## {datetime.now().strftime('%Y-%m-%d')} — Feature (reparado por doctor)
- **Agente:** doctor.py
- **Resultado:** {result}

{content}
"""
    with open("progress/history.md", "a", encoding="utf-8") as f:
        f.write(archive_entry)


def main():
    print("═" * 58)
    print("  HARNESS DOCTOR")
    print("═" * 58)

    data = load_features()
    features = data.get("features", [])
    current_md = read_current_md()
    in_progress = [f for f in features if f["status"] == "in_progress"]
    fixes = []

    # Issue 1: Más de un in_progress
    if len(in_progress) > 1:
        warn(f"Hay {len(in_progress)} features en in_progress. Dejando solo la de mayor id.")
        # Sort by id, keep highest, set others to blocked
        sorted_fp = sorted(in_progress, key=lambda x: x["id"])
        for f in sorted_fp[:-1]:
            f["status"] = "blocked"
            fixes.append(f"Feature #{f['id']} → blocked (duplicado)")
        save_features(data)
        in_progress = [sorted_fp[-1]]
        ok("Dejado solo el in_progress de mayor id")

    # Issue 2: Feature done pero current.md no vacío
    done_features = [f for f in features if f["status"] == "done"]
    if done_features and not is_current_md_empty(current_md):
        # Check if current.md refers to a done feature
        for f in done_features:
            if f"#{f['id']}" in current_md or f['name'] in current_md:
                warn(f"Feature #{f['id']} está done pero current.md no está vacío")
                archive_current_md(f['name'], "archived by doctor (feature was done)")
                empty_current_md()
                fixes.append(f"current.md vaciado (feature #{f['id']} ya estaba done)")
                ok("current.md vaciado y archivado")
                break

    # Issue 3: current.md dice "ninguna" pero hay in_progress
    if is_current_md_empty(current_md) and len(in_progress) == 1:
        f = in_progress[0]
        warn(f"current.md dice 'ninguna' pero feature #{f['id']} está in_progress")
        info("Esto es inconsistente. El agente debería haber inicializado current.md.")
        info("Puedes ejecutar ./harness/start.py para reiniciar, o continuar manualmente.")
        fixes.append(f"Inconsistencia: feature #{f['id']} in_progress pero current.md vacío")

    # Issue 4: No hay in_progress pero current.md NO está vacío
    if len(in_progress) == 0 and not is_current_md_empty(current_md):
        warn("No hay feature in_progress pero current.md tiene contenido")
        archive_current_md("unknown", "archived by doctor (no active session)")
        empty_current_md()
        fixes.append("current.md vaciado (no había sesión activa)")
        ok("current.md vaciado y archivado")

    print()
    if fixes:
        info(f"Reparaciones aplicadas: {len(fixes)}")
        for fix in fixes:
            print(f"  - {fix}")
    else:
        ok("No se encontraron problemas. El arnés está sano.")

    print("═" * 58)


if __name__ == "__main__":
    main()
