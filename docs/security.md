# Seguridad — Reglas de protección del proyecto

> El agente nunca debe comprometer la seguridad del sistema del usuario.
> Estas reglas son no negociables.

## Threat Model

### De quienes nos protegemos

| Amenaza | Descripción | Mitigación principal |
|---------|-------------|----------------------|
| **Agente comprometido** | Un agente de IA ejecuta código malicioso por error o manipulación | `set -euo pipefail`, validación de symlinks, sanitización de inputs |
| **Supply chain** | Dependencias o scripts del arnés modificados por terceros | Security checks en start/done, detección de secrets, no auto-aprobar |
| **Insider (desatención)** | Desarrollador comitea secrets o ejecuta comandos destructivos | `.gitignore` estricto, security-check.py, forbidding de `sudo`/`rm -rf` |
| **Path traversal / TOCTOU** | Symlinks o rutas relativas apuntan fuera del proyecto | Validación de `os.path.islink()`, path containment checks |

### Superficie de ataque

1. **Scripts del harness** (`harness/*.py`, `init.sh`): ejecutan con los permisos del usuario.
2. **`feature_list.json` y `progress/`**: escritura no controlada podría corromper estado o escalar a archivos del sistema.
3. **Código fuente del proyecto** (`src/`, `config/`, `.github/`): donde suelen residir secrets hardcodeados.
4. **Dependencias externas**: `requirements.txt`, `package.json`, `go.mod`.

---

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
- ✅ Usar `security-check.py` antes de cada commit para detectar filtraciones accidentales.

### R3 — Ejecución de comandos

- ❌ NO ejecutar comandos de red desconocidos (`curl | bash`, `wget | sh`).
- ❌ NO ejecutar `rm -rf` sin confirmación explícita del humano.
- ❌ NO ejecutar `sudo` ni comandos con privilegios elevados.
- ✅ Todo comando potencialmente destructivo debe ir en modo `--dry-run` primero.
- ✅ Todo script bash debe usar `set -euo pipefail` para fallar rápido ante errores.

### R4 — Datos sensibles en tests

- ❌ NO usar datos reales de usuarios en tests.
- ❌ NO incluir PII (emails reales, DNI, teléfonos) en fixtures o mocks.
- ✅ Usar datos sintéticos: `test@example.com`, `user-123`, etc.

### R5 — Dependencias

- ❌ NO añadir dependencias sin justificar en `feature_list.json`.
- ❌ NO instalar paquetes de fuentes no verificadas.
- ✅ Preferir stdlib. Si se necesita externo, documentar por qué.
- ✅ Revisar `requirements.txt` y lockfiles en cada PR.

---

## Hardening del arnés

### Validación de symlinks (TOCTOU prevention)

Todos los scripts del harness validan que `feature_list.json`, `progress/current.md` y `progress/history.md` **no sean symlinks** antes de leer o escribir:

```python
def _validate_not_symlink(path):
    if os.path.islink(path):
        sys.exit(1)
```

Esto previene que un atacante sustituya estos archivos por symlinks a `/etc/passwd` u otros del sistema.

### Path traversal prevention

`block.py --from-file` valida que la ruta objetivo resuelva **dentro del directorio del proyecto**:

```python
def _validate_path_in_project(path):
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(BASE_DIR)
    if not abs_path.startswith(abs_base + os.sep):
        sys.exit(1)
```

### Sanitización de inputs

`init.sh` sanitiza el nombre de paquete extraído de `requirements.txt` para prevenir code injection:

```bash
FIRST_PKG=$(head -n 1 requirements.txt | sed 's/[<>=!~].*//' | tr -d ' ')
SANITIZED=$(printf '%s' "$FIRST_PKG" | sed 's/[^a-zA-Z0-9_]//g')
```

Solo se permiten identificadores Python válidos (`[a-zA-Z_][a-zA-Z0-9_]*`).

---

## Verificación automatizada

El script `harness/security-check.py` se ejecuta automáticamente en:
- `./harness/start.py` (antes de empezar a trabajar).
- `./harness/done.py` (antes de cerrar la sesión).

**Por defecto está activado.** Desactivarlo requiere editar `feature_list.json` y cambiar `rules.security_checks` a `false`. Hazlo solo en entornos de desarrollo controlados y documenta el motivo.

### Qué comprueba

1. **Secrets hardcodeados** en `src/`, `config/`, `scripts/`, `.github/` y archivos de configuración (`docker-compose.yml`, `Dockerfile`, `.env.example`).
   - Patrones detectados: API keys, passwords, tokens, Bearer tokens, OpenAI keys (`sk-...`), AWS keys (`AKIA...`), GitHub PATs (`ghp_...`, `github_pat_...`), JWT tokens (`eyJ...`), URIs de bases de datos con credenciales, private keys.
2. **Archivos sensibles en `.gitignore`** (`.env`, `*.pem`, `.ssh/`, etc.).
3. **Comandos peligrosos** en scripts del proyecto (`rm -rf /`, `curl | bash`, `wget | bash`, `sudo`).
   - **Nota:** `harness/` ya NO está excluido del análisis. Los scripts del arnés son críticos y se escanean igual que el resto.
4. **Datos PII reales** en `tests/` (emails que no sean de dominios de ejemplo).

### Si encuentro un problema de seguridad

1. **NO** continúes con la feature.
2. Documenta el hallazgo en `progress/current.md`.
3. Ejecuta `./harness/block.py "Hallazgo de seguridad: [descripción]"`.
4. Informa inmediatamente al humano.

---

## Checklist de seguridad para nuevas features

- [ ] No se añaden secrets hardcodeados.
- [ ] No se ejecutan comandos con `sudo` o `rm -rf` sin confirmación.
- [ ] No se añaden dependencias sin justificar.
- [ ] `.gitignore` cubre nuevos archivos sensibles si se introducen.
- [ ] `security-check.py` pasa antes de declarar `done`.
- [ ] Se validan symlinks en archivos críticos si se añaden nuevos scripts del harness.
