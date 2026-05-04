#!/usr/bin/env python3
"""block.py — Bloquea una feature activa registrando el motivo.

Uso:
  ./harness/block.py "Motivo del bloqueo"
  ./harness/block.py --from-file progress/current.md  # usa la bitácora como motivo

El script:
  1. Cambia la feature in_progress a blocked en feature_list.json.
  2. Añade el motivo a progress/current.md.
  3. Archiva current.md en history.md.
  4. Vacía current.md.
"""

import argparse
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


def main():
    parser = argparse.ArgumentParser(description="Bloquea una feature activa")
    parser.add_argument("reason", nargs="?", default="", help="Motivo del bloqueo")
    parser.add_argument("--from-file", help="Ruta a archivo con el motivo (usa su contenido)")
    args = parser.parse_args()

    print("═" * 58)
    print("  HARNESS BLOCK")
    print("═" * 58)

    # 1. Cargar features
    data = load_features()
    features = data.get("features", [])

    in_progress = [f for f in features if f["status"] == "in_progress"]
    if not in_progress:
        fail("No hay ninguna feature in_progress. Nada que bloquear.")
        sys.exit(1)

    feature = in_progress[0]

    # 2. Determinar motivo
    reason = args.reason
    if args.from_file:
        if os.path.exists(args.from_file):
            with open(args.from_file, "r", encoding="utf-8") as f:
                reason = f.read()
        else:
            fail(f"Archivo no encontrado: {args.from_file}")
            sys.exit(1)

    if not reason.strip():
        warn("No se proporcionó motivo. Usa: ./harness/block.py \"motivo aquí\"")
        reason = "Bloqueado sin motivo especificado."

    # 3. Marcar como blocked
    print("── Paso 1: Marcando feature como blocked ───────────────")
    feature["status"] = "blocked"
    save_features(data)
    ok(f"Feature #{feature['id']} '{feature['name']}' → blocked")

    # 4. Añadir motivo a current.md
    print()
    print("── Paso 2: Registrando motivo ──────────────────────────")
    if os.path.exists("progress/current.md"):
        with open("progress/current.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## BLOQUEO ({datetime.now().isoformat(timespec='minutes')})\n")
            f.write(f"{reason}\n")
        ok("Motivo añadido a progress/current.md")
    else:
        warn("No existe progress/current.md")

    # 5. Archivar
    print()
    print("── Paso 3: Archivando sesión ───────────────────────────")
    if os.path.exists("progress/current.md"):
        with open("progress/current.md", "r", encoding="utf-8") as f:
            current_content = f.read()

        archive_entry = f"""
---

## {datetime.now().strftime('%Y-%m-%d')} — Feature {feature['id']}: {feature['name']}
- **Agente:** (ver progress/current.md)
- **Resultado:** blocked

{current_content}
"""
        with open("progress/history.md", "a", encoding="utf-8") as f:
            f.write(archive_entry)
        ok("Sesión archivada en progress/history.md")

    # 6. Vaciar current.md
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
    ok("Feature bloqueada correctamente.")
    info(f"Feature #{feature['id']} bloqueada.")
    print("═" * 58)


if __name__ == "__main__":
    main()
