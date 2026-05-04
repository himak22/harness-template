# Onboarding — Guía rápida para humanos

> Este documento es para **personas**, no para agentes de IA.
> Si eres un agente, lee `AGENTS.md` (o `OPENCODE.md` si usas OpenCode).

## ¿Qué es esto?

Este repositorio usa **Harness Engineering**: un sistema para que un agente de IA
y un humano trabajen juntos de forma ordenada, verificable y sin caos.

## Flujo de trabajo en 3 pasos

### 1. Definir el scope

Tú decides qué feature se implementa. Está documentada en `feature_list.json`.

```bash
# Ver qué hay pendiente
cat feature_list.json | grep -A 5 '"status": "pending"'
```

### 2. Decirle al agente que empiece

**Copia el mensaje de `PROMPT.md` y pégalo en el chat con tu IA.**

Es la única frase que necesitas. El prompt le dice a la IA:
- Que lea `AGENTS.md`
- Que ejecute `./harness/status.py`
- Que espere tu confirmación antes de implementar

Si prefieres, puedes personalizarlo:
```
"Implementa la feature #3"
```

Pero el prompt de `PROMPT.md` está diseñado para que la IA siga el protocolo correctamente desde el primer mensaje.

El agente:
1. Ejecuta `./harness/start.py` (o `./harness/start.py 3` si especificas id).
2. Te comunica su decisión: "Feature #3. Complejidad: media. Decisión: trabajo directo. Razón: 3 archivos, 4 criterios."
3. Tú confirmas (o pides que use subagentes).
4. El agente implementa, escribe tests, y actualiza `progress/current.md`.

### 3. Cerrar la sesión

Cuando el agente dice "Está listo":

```bash
./harness/done.py
```

Esto:
1. Ejecuta tests (obligatorio).
2. Ejecuta security-check (si está activado).
3. Marca la feature como `done`.
4. Archiva la bitácora en `progress/history.md`.

## Scripts útiles

| Script | Para qué sirve |
|--------|----------------|
| `./harness/status.py` | Ver estado rápido: feature activa, tests, próxima tarea. |
| `./harness/start.py` | Iniciar sesión sobre una feature. |
| `./harness/done.py` | Cerrar sesión (tests + verificaciones automáticas). |
| `./harness/block.py` | Bloquear una feature si algo falla. |
| `./harness/test.py` | Correr solo los tests (rápido, sin verificaciones extra). |
| `./harness/doctor.py` | Reparar inconsistencias en el estado del arnés. |

## Configuración

### Activar/desactivar security checks

Edita `feature_list.json`:

```json
{
  "rules": {
    "security_checks": true
  }
}
```

### Adaptar a tu stack

Lee `ADAPTING.md` y sigue la checklist.

## Estructura de archivos importantes

| Archivo | Qué contiene |
|---------|--------------|
| `feature_list.json` | Backlog de features. Tú lo editas para definir scope. |
| `progress/current.md` | Bitácora de la sesión activa. El agente lo actualiza. |
| `progress/history.md` | Historial de sesiones cerradas. Append-only. |
| `docs/architecture.md` | Cómo debe estar estructurado el código. |
| `docs/conventions.md` | Estilo de código y nombres. |
| `docs/decision-framework.md` | Criterios para decidir si el agente usa subagentes. |
| `docs/security.md` | Reglas de seguridad. |
| `CHECKPOINTS.md` | Lista de verificación que el revisor evalúa. |

## Si algo falla

1. **El agente no puede empezar:** Ejecuta `./harness/doctor.py` para reparar estado inconsistente.
2. **Tests fallan pero el código parece bien:** Ejecuta `./harness/test.py` para ver solo los tests.
3. **El agente se bloqueó:** Pídele que ejecute `./harness/block.py "motivo"`.
4. **init.sh falla:** Lee el output, corrige lo que dice, vuelve a ejecutar.

## Regla de oro

> **Una feature a la vez.** No mezcles cambios de varias features en la misma sesión.
> Si quieres cambiar de tarea, cierra la actual primero con `./harness/done.py` o `./harness/block.py`.
