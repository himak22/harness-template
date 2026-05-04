# ADAPTING.md — Checklist para adaptar el Harness a tu proyecto

> Lee esto entero antes de tocar código. Cada sección es obligatoria.

---

## 1. Nombre y propósito del proyecto

- [ ] Renombra la carpeta del template al nombre de tu proyecto.
- [ ] Abre `feature_list.json` y cambia `project`, `description` y `rules`.
- [ ] Añade al menos una feature con estado `pending`.

---

## 2. Stack y herramientas

Determina tu stack y adapta los archivos marcados:

| Archivo | Qué adaptar |
|---------|-------------|
| `init.sh` | Comando de ejecución de tests, versión mínima del runtime, dependencias a verificar. |
| `docs/conventions.md` | Estilo de código, nombres, estructura de archivos de TU stack. |
| `docs/verification.md` | Cómo correr tests en TU stack, smoke tests manuales. |
| `docs/architecture.md` | Capas de TU proyecto, dependencias permitidas, principios. |

### Ejemplo: si usas TypeScript/Node

```bash
# init.sh — cambiar la sección de tests
if [ -d "tests" ] || [ -d "src" ]; then
  if npm test 2>&1; then
    ok "Todos los tests pasan"
  else
    fail "Hay tests rotos"
    EXIT_CODE=1
  fi
fi
```

### Ejemplo: si usas Go

```bash
# init.sh — cambiar la sección de tests
go test ./... 2>&1
```

---

## 3. Estructura de directorios de tu app

- [ ] Crea tu estructura de código (`src/`, `app/`, `cmd/`, `lib/`, etc.).
- [ ] Asegúrate de que `docs/architecture.md` la documente.
- [ ] Asegúrate de que `CHECKPOINTS.md` C3 verifique que no hay archivos inesperados en esas carpetas.

---

## 4. Roles de agentes (opcional pero recomendado)

Los archivos en `.claude/agents/` son genéricos. Puedes ajustarlos si tu proyecto necesita roles adicionales:

- ¿Hay infraestructura (Terraform, Docker)? → Añade `infrastructure.md` en `.claude/agents/`.
- ¿Hay frontend y backend separados? → Añade `frontend.md` y `backend.md` implementers.
- ¿Necesitas un arquitecto para decisiones grandes? → Añade `architect.md`.

---

## 5. Primer arranque

- [ ] Ejecuta `./init.sh` en el proyecto adaptado.
- [ ] Debe terminar verde (posiblemente con warnings de que no hay tests todavía).
- [ ] Si falla, corrige antes de continuar.

---

## 6. Anti-patrones comunes al adaptar

- **NO** copies `src/` ni `tests/` del ejemplo de notas. Son específicos.
- **NO** dejes referencias a Python si tu stack es otro. Revisa `init.sh` y `docs/` con un grep.
- **NO** olvides vaciar `progress/history.md` (o déjalo con un placeholder).
- **NO** dejes el `feature_list.json` con features del ejemplo de notas.

---

## 7. Verificación final

Después de adaptar, ejecuta esta búsqueda para detectar restos del ejemplo:

```bash
grep -ri "notes" . --include="*.md" --include="*.json" --include="*.sh" --exclude-dir=".git"
```

Si hay coincidencias que no sean referencias explicativas al ejemplo, límpialas.
