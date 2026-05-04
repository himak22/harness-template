# AGENTS.md — Cómo trabajar en este repositorio

> **Para agentes de IA:** Lee solo la sección "Quick Start". El resto es referencia.
>
> **Si usas OpenCode:** Lee primero `OPENCODE.md` (instrucciones específicas de
> plataforma), luego vuelve aquí para el protocolo de trabajo.

---

## Quick Start (30 segundos)

```bash
# 1. Ver estado actual
./harness/status.py

# 2. Iniciar trabajo (como implementer)
./harness/start.py

# 3. COMUNICAR DECISIÓN al humano antes de tocar código
#    Lee docs/decision-framework.md y di:
#    "Feature #X. Complejidad: [baja/media/alta].
#     Decisión: [directo / explorar+directo / subagentes].
#     Razón: [criterio]."
#    Espera confirmación del humano.

# 4. Leer acceptance criteria y documentación de tu stack
#    docs/architecture.md, docs/conventions.md, docs/verification.md
#    docs/security.md

# 5. Implementar código + tests
#    (durante desarrollo, verifica rápido con ./harness/test.py)

# 6. Verificar antes de cerrar
./init.sh

# 7. Cerrar sesión (init.sh se ejecuta automáticamente; security-check también
#    si rules.security_checks es true en feature_list.json)
./harness/done.py
```

> **Si algo falla en el paso 6:** usa `./harness/block.py "motivo"` en lugar de `done.py`.

---

## Referencia completa

### Flujo de trabajo

```
./harness/status.py   → Briefing rápido (no toca nada)
./harness/start.py    → Inicia sesión: feature → in_progress, current.md, init.sh
./harness/done.py     → Cierra sesión: init.sh (obligatorio) → done, archiva
./harness/block.py    → Bloquea sesión: blocked, archiva con motivo
./harness/test.py     → Ejecuta solo los tests (rápido, para desarrollo iterativo)
./harness/doctor.py   → Repara inconsistencias en el estado del arnés
```

### Roles

| Rol | Qué hace | Cómo se activa |
|-----|----------|----------------|
| **implementer** | Edita `src/` y `tests/`. Implementa UNA feature. | `./harness/start.py` (por defecto) |
| **leader** | Orquesta. NO edita código. Lanza subagentes. | `./harness/start.py --role leader` |
| **reviewer** | Valida. NO edita código. Aprueba/rechaza. | `./harness/start.py --role reviewer` |

### Reglas duras

- **Una sola feature a la vez.** `start.py` lo valida. No edites `feature_list.json` a mano.
- **COMUNICA tu decisión antes de implementar.** Lee `docs/decision-framework.md`, analiza la complejidad, y di al humano: "Feature #X. Complejidad: [baja/media/alta]. Decisión: [directo / explorar+directo / subagentes]. Razón: [criterio]." Espera confirmación.
- **No cierres sin tests verdes.** `done.py` ejecuta `init.sh` automáticamente. Si falla, aborta.
- **No cierres sin security-check (si está activado).** `done.py` ejecuta `harness/security-check.py` automáticamente cuando `rules.security_checks` es `true` en `feature_list.json`. Si falla, aborta.
- **Documenta en `progress/current.md`** mientras trabajas, no al final.
- **No dejes el repo sucio.** Sin archivos temporales, logs de debug, ni TODOs sin contexto.
- **Si te bloqueas:** no inventes workaround. Ejecuta `./harness/block.py "motivo"`.

### Mapa de archivos

| Archivo | Cuándo leerlo |
|---------|---------------|
| `feature_list.json` | Siempre, al empezar |
| `progress/current.md` | Siempre, al empezar |
| `docs/decision-framework.md` | Antes de implementar (para decidir si usas subagentes) |
| `docs/architecture.md` | Antes de implementar |
| `docs/conventions.md` | Antes de escribir código |
| `docs/verification.md` | Antes de declarar done |
| `docs/security.md` | Antes de implementar y antes de cerrar |
| `CHECKPOINTS.md` | Para auto-evaluarte |

### Cierre de sesión manual (si los scripts fallan)

Solo si `./harness/done.py` o `./harness/block.py` no funcionan:

1. Ejecuta `./init.sh`.
2. Marca `status: "done"` (o `"blocked"`) en `feature_list.json`.
3. Mueve el contenido de `progress/current.md` al final de `progress/history.md`.
4. Vacía `progress/current.md` con la plantilla base.
