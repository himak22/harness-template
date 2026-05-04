# Harness Template

> Esqueleto genérico de **Harness Engineering** para proyectos de cualquier stack.
> Copia esta carpeta entera, renómbrala, y sigue `ADAPTING.md`.

## Qué incluye este template

```
.
├── AGENTS.md              # Punto de entrada para cualquier agente
├── CHECKPOINTS.md         # Criterios objetivos de calidad
├── CLAUDE.md              # Instrucciones específicas para Claude
├── feature_list.json      # Backlog estructurado (una a la vez)
├── init.sh                # Verificación ejecutable del entorno
├── progress/
│   ├── current.md         # Estado de la sesión activa
│   └── history.md         # Bitácora append-only
├── docs/
│   ├── architecture.md    # Qué significa "buen trabajo" en TU proyecto
│   ├── conventions.md     # Estilo, nombres, estructura de TU stack
│   └── verification.md    # Cómo demostrar que funciona en TU proyecto
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
5. Lanza el agente líder con: "Implementa la siguiente feature pendiente."

## Flujo de trabajo

```
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│  Humano │────→│ feature_list│────→│  Líder   │────→│Implementer│
│ (scope) │     │  (una sola) │     │(orquesta)│     │ (código)  │
└─────────┘     └─────────────┘     └────┬─────┘     └────┬─────┘
                                         │                │
                                         │                ↓
                                         │           progress/impl_*.md
                                         │                │
                                         ↓                ↓
                                    ┌──────────┐    ┌──────────┐
                                    │ Reviewer │←───│  Tests   │
                                    │(validar) │    │ (verdes) │
                                    └────┬─────┘    └──────────┘
                                         │
                                         ↓
                                    APPROVED → feature → done
```

## Principios inmutables

1. **Una feature a la vez.** `init.sh` lo valida.
2. **Estado en disco, no en chat.** Todo vive en `progress/`.
3. **Verificación ejecutable.** `./init.sh` es la única fuente de verdad.
4. **Separación de roles.** Líder no implementa, implementador no se autoaprueba, revisor no edita.
5. **Anti teléfono-descompuesto.** Subagentes escriben a archivo, devuelven referencias.

## Adaptar a tu stack

Ver `ADAPTING.md` para la checklist completa.
