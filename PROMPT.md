# Prompt de activación para la IA

> Copia el bloque de abajo y pégalo en el chat con tu agente de IA.
> Es la única frase que necesitas para empezar a trabajar.

---

```
Estamos trabajando con Harness Engineering.

Lee AGENTS.md para entender el protocolo.
Luego ejecuta ./harness/status.py para ver el estado actual.

Trabajamos juntos tú (IA) y yo (humano).
Una feature a la vez. Estado en disco, no en chat.
Verificación ejecutable con ./init.sh.

Cuando estés listo, dime qué feature está pendiente y cuál es tu decisión sobre cómo implementarla (directo, explorar+directo, o subagentes).
```

---

## ¿Por qué este prompt?

Tu IA no sabe que este repo usa Harness Engineering a menos que se lo digas. Este prompt:

1. **Establece el framework** — "Harness Engineering" le dice a la IA que hay un protocolo.
2. **Apunta al archivo correcto** — `AGENTS.md` es el punto de entrada diseñado para agentes.
3. **Obliga a verificar estado** — `./harness/status.py` evita que la IA asuma que empieza de cero.
4. **Define las reglas del juego** — Una feature a la vez, estado en disco, verificación ejecutable.
5. **Pide la decisión** — Fuerza a la IA a comunicar su análisis antes de tocar código.

## Variaciones

### Si quieres que implemente una feature específica:

```
Estamos trabajando con Harness Engineering.

Lee AGENTS.md, luego ejecuta ./harness/start.py para la feature #3.
Analiza la complejidad y dime tu decisión antes de implementar.
```

### Si solo quieres explorar el repo:

```
Estamos trabajando con Harness Engineering.

Lee AGENTS.md y ./harness/status.py.
Explora el repo y dime: ¿qué features están pendientes? ¿En qué estado quedó la última sesión?
No toques código, solo investiga.
```

### Si usas Claude Code (en lugar de OpenCode):

Reemplaza `AGENTS.md` por `CLAUDE.md`:

```
Estamos trabajando con Harness Engineering.

Lee CLAUDE.md para entender tu rol, luego ejecuta ./harness/status.py.
```

> **Nota:** Nuestro template usa `OPENCODE.md` para OpenCode y `AGENTS.md` como protocolo general. Si tu plataforma soporta `CLAUDE.md` (Claude Code), renombra `OPENCODE.md` a `CLAUDE.md`.
