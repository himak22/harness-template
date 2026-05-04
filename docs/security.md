# Seguridad — Reglas de protección del proyecto

> El agente nunca debe comprometer la seguridad del sistema del usuario.
> Estas reglas son no negociables.

## Reglas duras

### R1 — No tocar fuera del proyecto

- ❌ NO leer archivos fuera del directorio de trabajo.
- ❌ NO escribir archivos fuera del directorio de trabajo.
- ❌ NO ejecutar comandos que afecten el sistema global (instalar paquetes globales, modificar `/etc`, etc.).

### R2 — Secrets y credenciales

- ❌ NO hardcodear API keys, passwords, tokens ni secrets en el código.
- ❌ NO commitear archivos `.env`, `credentials.json`, `*.pem`, `*.key`.
- ✅ Usar variables de entorno o archivos de configuración en `.gitignore`.
- ✅ Si un test necesita un secret, usar un valor dummy/fake.

### R3 — Ejecución de comandos

- ❌ NO ejecutar comandos de red desconocidos (`curl | bash`, `wget | sh`).
- ❌ NO ejecutar `rm -rf` sin confirmación explícita del humano.
- ❌ NO ejecutar `sudo` ni comandos con privilegios elevados.
- ✅ Todo comando potencialmente destructivo debe ir en modo `--dry-run` primero.

### R4 — Datos sensibles en tests

- ❌ NO usar datos reales de usuarios en tests.
- ❌ NO incluir PII (emails reales, DNI, teléfonos) en fixtures o mocks.
- ✅ Usar datos sintéticos: `test@example.com`, `user-123`, etc.

### R5 — Dependencias

- ❌ NO añadir dependencias sin justificar en `feature_list.json`.
- ❌ NO instalar paquetes de fuentes no verificadas.
- ✅ Preferir stdlib. Si se necesita externo, documentar por qué.

## Verificación automatizada

El script `harness/security-check.py` se ejecuta automáticamente en:
- `./harness/start.py` (antes de empezar a trabajar).
- `./harness/done.py` (antes de cerrar la sesión).

**Pero es opcional.** Puedes desactivarlo si lo necesitas.

### Cómo desactivar los security checks

Edita `feature_list.json` y cambia `rules.security_checks` a `false`:

```json
{
  "rules": {
    "security_checks": false
  }
}
```

Por defecto está en `true`. Úsalo con responsabilidad.

### Qué comprueba

1. Que no hay secrets hardcodeados en `src/`.
2. Que archivos sensibles están en `.gitignore`.
3. Que no hay comandos peligrosos en scripts del proyecto.

## Si encuentro un problema de seguridad

1. **NO** continúo con la feature.
2. Documento el hallazgo en `progress/current.md`.
3. Ejecuto `./harness/block.py "Hallazgo de seguridad: [descripción]"`.
4. Te informo inmediatamente.
