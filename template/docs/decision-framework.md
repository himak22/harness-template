# Framework de Decisión — ¿Uso subagentes?

> Antes de tocar código, el agente (yo) DEBE comunicar su decisión al humano.
> Este archivo define los criterios objetivos. La decisión no es subjetiva.

## Mi obligación

**SIEMPRE, sin excepciones**, antes de implementar una feature te digo:

> "He analizado la feature #X. Complejidad: [baja/media/alta]. Decisión: [trabajo directo / subagentes]. Razón: [criterio aplicado]."

No empiezo a escribir código hasta que tú veas esa línea.

---

## Criterios objetivos

### Complejidad BAJA → Trabajo directo (sin subagentes)

Aplica cuando TODAS estas condiciones se cumplen:
- [ ] La feature toca ≤2 archivos.
- [ ] Los acceptance criteria son ≤3 ítems.
- [ ] No requiere investigación previa (ya sé cómo hacerlo).
- [ ] No hay dependencias con otras features pendientes.

**Ejemplo:** "Añadir campo `email` al modelo User."

**Mi mensaje a ti:**
> "Feature #4. Complejidad: baja. Decisión: trabajo directo. Razón: 2 criterios, toca 1 archivo de modelo y 1 test. No requiere investigación."

### Complejidad MEDIA → Exploración + trabajo directo

Aplica cuando AL MENOS UNA de estas condiciones se cumple:
- [ ] La feature toca 3-4 archivos.
- [ ] Los acceptance criteria son 4-6 ítems.
- [ ] Requiere investigación breve (nueva librería, patrón desconocido).
- [ ] Hay una decisión técnica ambigua (¿usar A o B?).

**Mi acción:**
1. Lanzo 1-2 explorers en paralelo para investigar.
2. Espero resultados.
3. Implemento yo directamente con lo aprendido.

**Ejemplo:** "Añadir paginación a la API. ¿Cursor-based o offset-based?"

**Mi mensaje a ti:**
> "Feature #7. Complejidad: media. Decisión: exploración + trabajo directo. Razón: hay una decisión ambigua (cursor vs offset). Lanzaré 2 explorers para investigar, luego implemento yo."

### Complejidad ALTA → Subagentes completos (leader mode)

Aplica cuando AL MENOS UNA de estas condiciones se cumple:
- [ ] La feature toca ≥5 archivos.
- [ ] Los acceptance criteria son ≥7 ítems.
- [ ] Es un refactor que cambia la arquitectura.
- [ ] Requiere investigación profunda o spike técnico.
- [ ] Hay riesgo de romper features existentes.

**Mi acción:**
1. Actúo como `leader` (no toco código).
2. Lanzo explorers → implementer → reviewer.
3. Coordino y cierro.

**Ejemplo:** "Migrar de REST a GraphQL."

**Mi mensaje a ti:**
> "Feature #12. Complejidad: alta. Decisión: subagentes completos. Razón: refactor arquitectónico, toca 6+ archivos, riesgo de romper tests existentes. Actuaré como leader: explorers → implementer → reviewer."

---

## Tabla resumen

| Complejidad | Archivos | Acceptance | Investigación | Decisión |
|-------------|----------|------------|---------------|----------|
| Baja | ≤2 | ≤3 | No | Directo |
| Media | 3-4 | 4-6 | Breve | Explorar + directo |
| Alta | ≥5 | ≥7 | Profunda | Subagentes completos |

---

## Anti-patrones (yo no debo hacer esto)

- ❌ Decidir "a ojo" sin contar archivos o criterios.
- ❌ Lanzar subagentes para una feature trivial "porque sí".
- ❌ Trabajar directo en una feature compleja "para ir más rápido".
- ❌ No comunicar la decisión antes de empezar.
