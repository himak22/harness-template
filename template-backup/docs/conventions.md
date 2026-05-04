# Convenciones de código

> Homogeneidad extrema. La IA predice mejor cuando el repositorio se parece
> a sí mismo en todas partes.

## Estilo

- **Versión:** Define tu versión mínima de lenguaje/runtime.
- **Formato:** Define tu guía de estilo (PEP 8, Prettier, gofmt, etc.) y
  longitud máxima de línea.
- **Imports:** Orden de imports (stdlib → externas → locales).
- **Strings:** Comillas dobles o simples, pero **consistentes**.
- **Interpolación:** f-strings, template literals, etc. Evitar concatenación
  manual.

## Nombres

| Tipo                    | Convención        | Ejemplo               |
|-------------------------|-------------------|-----------------------|
| Módulos / archivos      | `snake_case`      | `notes.py`            |
| Clases / tipos          | `PascalCase`      | `Note`                |
| Funciones / variables   | `snake_case`      | `load_notes`          |
| Constantes              | `UPPER_SNAKE`     | `DEFAULT_PATH`        |
| Privadas                | prefijo `_`       | `_internal_helper`    |

> Adapta esta tabla a las convenciones de tu stack.

## Estructura de archivo

Define un encabezado estándar para cada archivo de código:

```python
"""Una línea describiendo el propósito del módulo."""
# imports ordenados
```

## Tests

- Un archivo de test por módulo principal.
- Nombres descriptivos: `test_load_returns_empty_when_file_missing`.
- Cada test usa entornos temporales reales y limpia tras de sí.
- Cubre camino feliz + al menos un camino de error.

## Manejo de errores

Define excepciones/errores de dominio en un lugar central:

```python
class DomainError(Exception):
    """Base para errores del dominio."""

class NotFound(DomainError):
    """Se lanza cuando se busca un recurso inexistente."""
```

La interfaz de usuario captura excepciones del dominio, imprime mensaje a
stderr y sale con código != 0. Nunca propaga stack traces al usuario final.

## Comentarios

Por defecto **no** se escriben. Solo se permiten cuando explican un *por qué*
no obvio (workaround documentado, invariante sutil). Los nombres deben hacer
el resto.
