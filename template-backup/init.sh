#!/usr/bin/env bash
# init.sh — Verificación e inicialización del entorno
#
# Este script lo ejecuta el agente al COMENZAR una sesión y antes de
# declarar cualquier tarea como `done`. Si falla, la sesión no debe avanzar.
#
# Salida esperada: códigos de salida claros y bloques marcados con [OK]/[FAIL].
# Este template detecta tu stack automáticamente. Si tu stack no está soportado,
# edita la sección "Detectar stack y ejecutar tests".

set -u
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()    { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
fail()  { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }

EXIT_CODE=0

echo "── 1. Verificando entorno ─────────────────────────────"

# Python disponible (usado por init.sh mismo para validar JSON)
if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 no está instalado (se necesita para validar feature_list.json)"
  exit 1
fi
ok "python3 disponible"

# Detectar stack y verificar runtime principal
STACK="unknown"
if [ -f "go.mod" ]; then
  STACK="go"
  if ! command -v go >/dev/null 2>&1; then
    fail "go no está instalado"
    exit 1
  fi
  ok "go -> $(go version)"
elif [ -f "package.json" ]; then
  STACK="node"
  if ! command -v node >/dev/null 2>&1; then
    fail "node no está instalado"
    exit 1
  fi
  ok "node -> $(node --version)"
  if ! command -v npm >/dev/null 2>&1; then
    fail "npm no está instalado"
    exit 1
  fi
  ok "npm -> $(npm --version)"
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -d "src" ]; then
  STACK="python"
  PY_VERSION_OK=$(python3 -c 'import sys; print(int(sys.version_info >= (3, 9)))')
  if [ "$PY_VERSION_OK" != "1" ]; then
    fail "Se requiere Python >= 3.9"
    exit 1
  fi
  ok "python3 >= 3.9"
elif [ -f "Cargo.toml" ]; then
  STACK="rust"
  if ! command -v cargo >/dev/null 2>&1; then
    fail "cargo no está instalado"
    exit 1
  fi
  ok "cargo -> $(cargo --version)"
else
  warn "No se detectó stack conocido (go.mod, package.json, requirements.txt/pyproject.toml, Cargo.toml)"
fi

echo ""
echo "── 2. Verificando archivos base del arnés ──────────────"

for f in AGENTS.md feature_list.json progress/current.md docs/architecture.md docs/conventions.md docs/verification.md CHECKPOINTS.md; do
  if [ ! -f "$f" ]; then
    fail "Falta archivo base: $f"
    EXIT_CODE=1
  else
    ok "Existe $f"
  fi
done

echo ""
echo "── 3. Validando feature_list.json ──────────────────────"

python3 - <<'PY'
import json, sys
try:
    data = json.load(open("feature_list.json"))
    valid = {"pending", "in_progress", "done", "blocked"}
    in_progress = [f for f in data["features"] if f["status"] == "in_progress"]
    if len(in_progress) > 1:
        print(f"[FAIL]  Hay {len(in_progress)} features en in_progress (máximo 1)")
        sys.exit(1)
    for f in data["features"]:
        if f["status"] not in valid:
            print(f"[FAIL]  Estado inválido en feature {f['id']}: {f['status']}")
            sys.exit(1)
    print(f"[OK]    feature_list.json válido ({len(data['features'])} features)")
except Exception as e:
    print(f"[FAIL]  feature_list.json inválido: {e}")
    sys.exit(1)
PY

if [ $? -ne 0 ]; then EXIT_CODE=1; fi

echo ""
echo "── 4. Ejecutando tests ─────────────────────────────────"

# Detectar y ejecutar tests según stack
if [ "$STACK" == "go" ]; then
  if go test ./... 2>&1; then
    ok "Todos los tests pasan"
  else
    fail "Hay tests rotos"
    EXIT_CODE=1
  fi
elif [ "$STACK" == "node" ]; then
  if npm test 2>&1; then
    ok "Todos los tests pasan"
  else
    fail "Hay tests rotos"
    EXIT_CODE=1
  fi
elif [ "$STACK" == "python" ]; then
  if [ -d "tests" ]; then
    if python3 -m unittest discover -s tests -v 2>&1; then
      ok "Todos los tests pasan"
    else
      fail "Hay tests rotos"
      EXIT_CODE=1
    fi
  else
    warn "Carpeta tests/ no existe todavía"
  fi
elif [ "$STACK" == "rust" ]; then
  if cargo test 2>&1; then
    ok "Todos los tests pasan"
  else
    fail "Hay tests rotos"
    EXIT_CODE=1
  fi
else
  warn "No se ejecutaron tests (stack no detectado o no soportado)"
fi

echo ""
echo "── 5. Resumen ──────────────────────────────────────────"

if [ $EXIT_CODE -eq 0 ]; then
  ok "Entorno listo. Puedes empezar a trabajar."
else
  fail "Entorno NO está listo. Resuelve los errores antes de avanzar."
fi

exit $EXIT_CODE
