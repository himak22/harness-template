# Harness Template

> Esqueleto genérico de **Harness Engineering** para proyectos de cualquier stack.
> Copia esta carpeta entera, renómbrala, y sigue `ADAPTING.md`.

## Qué incluye este template

```
.
├── PROMPT.md              # Prompt de activación: qué decirle a tu IA para empezar
├── AGENTS.md              # Punto de entrada para cualquier agente (Quick Start + Referencia)
├── CHECKPOINTS.md         # Criterios objetivos de calidad
├── OPENCODE.md            # Instrucciones específicas para OpenCode (equivalente a CLAUDE.md)
├── feature_list.json      # Backlog estructurado (una a la vez)
├── init.sh                # Verificación ejecutable del entorno
├── harness/               # Scripts de orquestación del flujo de trabajo
│   ├── status.py          # Briefing rápido del estado del proyecto
│   ├── start.py           # Inicia sesión: feature → in_progress + current.md + init.sh
│   ├── done.py            # Cierra sesión: security-check + init.sh → done + archiva
│   ├── block.py           # Bloquea sesión: blocked + archiva con motivo
│   ├── test.py            # Ejecuta solo los tests (rápido, para desarrollo iterativo)
│   ├── doctor.py          # Repara inconsistencias en el estado del arnés
│   └── security-check.py  # Verifica secrets, .gitignore, comandos peligrosos
├── progress/
│   ├── current.md         # Estado de la sesión activa
│   └── history.md         # Bitácora append-only
├── docs/
│   ├── architecture.md       # Qué significa "buen trabajo" en TU proyecto
│   ├── conventions.md        # Estilo, nombres, estructura de TU stack
│   ├── verification.md       # Cómo demostrar que funciona en TU proyecto
│   ├── decision-framework.md # Criterios objetivos para decidir si usar subagentes
│   ├── security.md           # Reglas de seguridad no negociables
│   └── onboarding.md         # Guía rápida para humanos
└── .claude/agents/
    ├── leader.md          # Orquestador (no toca código)
    ├── implementer.md     # Trabajador (una feature, tests, verificación)
    └── reviewer.md        # Juez (aprobar/rechazar, no editar)
```

## Qué NO incluye (lo añades tú)

- Código fuente de tu aplicación (`src/`, `app/`, `lib/`, etc.)
- Tests (siguiendo las reglas de `docs/verification.md`)
- Dependencias (`package.json`, `requirements.txt`, `go.mod`, etc.)
- Configuración de CI/CD

## Cómo empezar

1. Copia esta carpeta: `cp -r template mi-proyecto`
2. Lee `ADAPTING.md` y sigue la checklist.
3. Ejecuta `./init.sh`. Debe terminar verde antes de tocar código.
4. Abre `feature_list.json` y añade tu primera feature.
5. **Abre `PROMPT.md`, copia el mensaje, y pégalo en el chat con tu IA.**
   Eso es todo lo que necesitas decirle para empezar.

## Flujo de trabajo con los scripts

```
Humano define scope → feature_list.json
                           ↓
                   ./harness/start.py
                           ↓
              ┌────────────┴────────────┐
              │   implementer / leader   │
              │     (trabaja en src/)    │
              └────────────┬────────────┘
                           ↓
                    ./harness/done.py
                           ↓
              (init.sh automático → verde → done)
                           ↓
              ┌────────────┴────────────┐
              │        reviewer          │
              │    (valida CHECKPOINTS)  │
              └──────────────────────────┘
```

## Scripts de orquestación (`harness/`)

| Script | Cuándo usarlo | Qué hace |
|--------|---------------|----------|
| `status.py` | Al entrar al repo | Muestra feature en curso, próxima pending, estado de init.sh, tests. |
| `start.py` | Antes de trabajar | Marca feature como in_progress, inicializa current.md, ejecuta security-check + init.sh. |
| `done.py` | Al terminar | Ejecuta security-check + init.sh (obligatorios), marca done, archiva en history.md. |
| `block.py` | Si te bloqueas | Marca blocked, registra motivo, archiva en history.md. |
| `test.py` | Durante desarrollo | Ejecuta solo los tests, sin verificaciones extra. Rápido e iterativo. |
| `doctor.py` | Cuando algo falla | Repara inconsistencias: in_progress duplicados, current.md desincronizado, etc. |
| `security-check.py` | Automático | Busca secrets, valida .gitignore, detecta comandos peligrosos. |

> **Los scripts te protegen de ti mismo:** `done.py` NO cierra si init.sh falla. `start.py` NO inicia si ya hay una sesión activa.

## Principios inmutables

1. **Una feature a la vez.** `start.py` y `init.sh` lo validan.
2. **Estado en disco, no en chat.** Todo vive en `progress/`.
3. **Verificación ejecutable.** `./init.sh` es la única fuente de verdad.
4. **Separación de roles.** Líder no implementa, implementador no se autoaprueba, revisor no edita.
5. **Anti teléfono-descompuesto.** Subagentes escriben a archivo, devuelven referencias.

## Adaptar a tu stack

Ver `ADAPTING.md` para la checklist completa.
