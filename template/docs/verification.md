# Verificación — Cómo demostrar que el trabajo funciona

> Regla de oro: **el agente no dice "funciona", lo demuestra**.
> Toda feature termina con evidencia ejecutable, no con afirmaciones.

## Niveles de verificación

### Nivel 1 — Tests unitarios (obligatorio)

Toda función pública tiene al least un test que:

1. Cubre el camino feliz.
2. Cubre al menos un camino de error si la función puede fallar.

Comando de ejecución (adapta a tu stack):
```bash
# Python
python3 -m unittest discover -s tests -v

# Node / Jest
npm test

# Go
go test ./...
```

### Nivel 2 — Test de integración (obligatorio para features de UI / API)

Las features que añaden comandos o endpoints se verifican ejecutando la
interfaz real contra un entorno temporal:

```python
import subprocess, tempfile, os
with tempfile.TemporaryDirectory() as d:
    env = {**os.environ, "CONFIG_PATH": os.path.join(d, "config.json")}
    out = subprocess.check_output(
        ["python3", "-m", "src.cli", "comando", "arg"],
        env=env, text=True,
    )
    assert "resultado esperado" in out
```

### Nivel 3 — Smoke test manual (opcional pero recomendado)

Antes de cerrar la sesión, ejecuta un flujo end-to-end con datos temporales.

## Anti-patrones (no hacer)

- ❌ "He añadido el comando, debería funcionar." → falta test ejecutable.
- ❌ Test que solo verifica que la función no lanza excepción. → tiene que
  comprobar el resultado concreto.
- ❌ Mocks del filesystem o red sin justificación. → usa entornos temporales reales.
- ❌ Marcar la feature como `done` sin pasar `./init.sh`.

## Verificación final antes de cerrar

```bash
./init.sh           # debe terminar con [OK] Entorno listo
```

Si `./init.sh` está rojo, **no** marques nada como `done`. Anota el bloqueo
en `progress/current.md` con estado `blocked` en `feature_list.json`.
