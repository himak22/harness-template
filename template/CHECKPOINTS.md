# CHECKPOINTS — Evaluación del estado final

> En sistemas multi-agente no se evalúa el camino, se evalúa el destino.
> Estos son los checkpoints objetivos que un juez (humano o IA) puede usar
> para decidir si el proyecto está sano.

## C1 — El arnés está completo

- [ ] Existen los 5 archivos base: `PROMPT.md`, `AGENTS.md`, `init.sh`, `feature_list.json`,
      `progress/current.md`.
- [ ] Existen los 5 docs: `docs/architecture.md`, `docs/conventions.md`,
      `docs/verification.md`, `docs/decision-framework.md`, `docs/security.md`.
- [ ] `./init.sh` termina con exit code 0.

## C2 — El estado es coherente

- [ ] Como mucho una feature en `in_progress` en `feature_list.json`.
- [ ] Toda feature `done` tiene tests asociados que pasan.
- [ ] `progress/current.md` está vacío o describe la sesión activa
      (no contiene basura de sesiones anteriores).

## C3 — El código respeta la arquitectura

- [ ] Las carpetas de código fuente solo contienen los módulos previstos en
      `docs/architecture.md`.
- [ ] No se añaden dependencias externas sin justificación documentada.
- [ ] No hay logs de debug sueltos, ni TODOs sin contexto.

## C4 — La verificación es real

- [ ] La carpeta de tests tiene al menos un test por módulo principal.
- [ ] Los tests usan entornos temporales reales (no mocks de filesystem,
      red, etc. salvo que `docs/verification.md` lo permita explícitamente).
- [ ] El comando de tests definido en `docs/verification.md` muestra > 0 tests
      y todos verdes.

## C5 — La sesión se cerró bien

- [ ] No hay archivos sin trackear sospechosos (`*.tmp`, `__pycache__`,
      `node_modules` fuera del `.gitignore` o similar).
- [ ] `progress/history.md` tiene una entrada por la última sesión.
- [ ] La última feature trabajada está reflejada en su estado correcto.

## C6 — Seguridad (solo si está activada)

> Si `rules.security_checks` en `feature_list.json` es `false`, este checkpoint se salta.

- [ ] `./harness/security-check.py` termina con exit code 0 (o `security_checks: false`).
- [ ] No hay secrets hardcodeados en `src/`.
- [ ] Archivos sensibles (`.env`, `*.pem`, etc.) están en `.gitignore`.
- [ ] No hay comandos peligrosos (`rm -rf /`, `curl | bash`, `sudo`) en scripts del proyecto.

---

**Cómo usar este archivo:** un agente revisor (`.claude/agents/reviewer.md`)
recorre cada checkbox, marca `[x]` o `[ ]`, y rechaza el cierre de sesión
si quedan boxes vacíos en C1-C6.
