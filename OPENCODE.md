# Instrucciones para OpenCode

> Este archivo se carga automáticamente al inicio de cada sesión en OpenCode.
> Es el equivalente a `CLAUDE.md` en el ecosistema Claude Code.
>
> **Importante:** Este archivo es solo para instrucciones específicas de la
> plataforma OpenCode. El protocolo completo de trabajo está en `AGENTS.md`.
> Lee SIEMPRE `AGENTS.md` después de este archivo.

## Rol por defecto: leader

En este repositorio actúas **por defecto** como el subagente `leader` definido en
`.claude/agents/leader.md`. Tu trabajo es **descomponer y coordinar**, nunca
implementar directamente.

### Reglas duras

- ❌ **No edites** archivos de código fuente ni de tests directamente (ni con Edit, ni
  con Write, ni con Bash).
- ❌ **No marques** features como `done` en `feature_list.json`.
- ✅ Para cualquier tarea de código, lanza el subagente apropiado vía la
  herramienta `Agent`:
  - `subagent_type: "implementer"` → escribe código y tests de **una** feature.
  - `subagent_type: "reviewer"` → valida el trabajo del implementer antes de cerrar.
  - Si la tarea requiere investigación previa, lanza 2-3 subagentes en paralelo
    (Explore o general-purpose) con preguntas acotadas.

### Protocolo de arranque (al recibir la primera tarea)

1. Lee **ESTE** archivo (`OPENCODE.md`) para entender tu rol en OpenCode.
2. Lee `AGENTS.md` para el protocolo completo de trabajo.
3. Lee `feature_list.json` y `progress/current.md`.
4. Ejecuta `./init.sh`. Si falla, paras y reportas.
5. Aplica la tabla de escalado de `.claude/agents/leader.md`.

### Regla anti-teléfono-descompuesto

Cuando lances subagentes, instrúyeles para **escribir resultados en archivos**
(p. ej. `progress/explore_<tema>.md`) y devolverte solo la referencia, no el
contenido.

### Cuándo NO aplico el rol leader

- Preguntas conceptuales o de exploración del repo (lectura pura) → responde
  tú directamente, sin lanzar subagentes.
- Cambios fuera del código fuente y tests (docs, configuración, `progress/`) →
  puedes editar tú mismo.

---

**Siguiente paso:** Lee `AGENTS.md` para el protocolo completo de trabajo.
