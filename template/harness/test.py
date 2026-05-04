#!/usr/bin/env python3
"""test.py — Ejecuta los tests del proyecto de forma rápida.

Uso: ./harness/test.py

Este script es para desarrollo iterativo. Solo ejecuta los tests,
sin verificar archivos base, feature_list.json, etc.
Para verificación completa usa ./init.sh.
"""

import os
import subprocess
import sys

# Determinar directorio base del proyecto (padre de harness/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
os.chdir(BASE_DIR)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"


def ok(msg): print(f"{GREEN}[OK]{NC}    {msg}")
def fail(msg): print(f"{RED}[FAIL]{NC}  {msg}")
def warn(msg): print(f"{YELLOW}[WARN]{NC}  {msg}")


def detect_stack():
    if os.path.exists("go.mod"):
        return "go"
    if os.path.exists("package.json"):
        return "node"
    if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml") or os.path.exists("src"):
        return "python"
    if os.path.exists("Cargo.toml"):
        return "rust"
    return "unknown"


def run_tests(stack):
    if stack == "go":
        return subprocess.run(["go", "test", "./..."])
    elif stack == "node":
        return subprocess.run(["npm", "test"])
    elif stack == "python":
        if os.path.exists("tests"):
            return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
        else:
            warn("No tests/ directory found")
            return subprocess.CompletedProcess(args=[], returncode=0)
    elif stack == "rust":
        return subprocess.run(["cargo", "test"])
    else:
        warn("No stack detected. Cannot run tests.")
        return subprocess.CompletedProcess(args=[], returncode=0)


def main():
    print("═" * 58)
    print("  HARNESS TEST")
    print("═" * 58)

    stack = detect_stack()
    info_msg = f"Stack detectado: {stack}"
    print(f"{YELLOW}[INFO]{NC}  {info_msg}")
    print()

    result = run_tests(stack)

    print()
    if result.returncode == 0:
        ok("Tests pasaron")
    else:
        fail("Tests FALLARON")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
