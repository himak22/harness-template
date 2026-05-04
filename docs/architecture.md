# Arquitectura — Qué significa "hacer un buen trabajo"

> Este documento define el estándar de calidad. Los agentes revisores
> evalúan código contra este archivo. Si no está aquí, no es un requisito.

## Principios

1. **Capas claras.** Define las capas de tu proyecto y mantén la lista corta:
   - Ejemplo: `storage.py`, `domain.py`, `cli.py`.
   No introducir capas adicionales (servicios, repositorios, ORMs) hasta que
   haya una razón concreta documentada en `feature_list.json`.

2. **Dependencias controladas.** Lista las dependencias externas permitidas.
   Si una feature requiere una nueva dependencia, primero se discute
   (estado `blocked`).

3. **Errores explícitos.** Las funciones que pueden fallar lanzan excepciones
   nombradas o devuelven `Result`/`Error`, nunca valores ambiguos como `None`
   sin documentar.

4. **Inmutabilidad por defecto.** Preferir estructuras inmutables. Modificar =
   crear una nueva instancia.

5. **Atomicidad en operaciones críticas.** Toda escritura destructiva debe ser
   atómica o transaccional.

## Flujo de datos

```
usuario  ─→  <interfaz> (CLI / API / UI)
               │
               ├─ construye <modelo de dominio>
               │
               └─→  <persistencia>
                        │
                        └─→  <almacenamiento>
```

## Qué NO hacer

- No usar `print()` / `console.log` para errores. Usa stderr y exit code != 0.
- No mezclar IO con lógica de dominio.
- No leer/escribir recursos externos en cada operación dentro de un bucle.
  Carga al inicio, modifica en memoria, guarda al final.
- No añadir sistemas de configuración globales sin justificar.
