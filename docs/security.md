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

## Seguridad de aplicación web

> **Importante:** El arnés detecta malas prácticas y vulnerabilidades **básicas**, pero NO sustituye un pentest ni un SAST profesional. Si construyes una aplicación web, estos checks son tu primera línea de defensa, no la única.

### Qué NO detecta security-check.py

| Vulnerabilidad | Ejemplo de código inseguro | Cómo prevenirlo |
|----------------|---------------------------|-----------------|
| **SQL Injection** | `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")` | Usa ORM o queries parametrizadas: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))` |
| **XSS (Cross-Site Scripting)** | `return f"<div>{request.form['comment']}</div>"` | Escapa todo output del usuario con la función de tu framework (`escape()`, `htmlspecialchars()`) |
| **Command Injection** | `os.system(f"ping {user_input}")` | Nunca concatenes input del usuario en comandos del sistema. Usa listas de argumentos: `subprocess.run(["ping", user_input])` |
| **CSRF** | Formulario sin token CSRF | Usa el mecanismo CSRF de tu framework (Django, Flask-WTF, Express csurf) |
| **Insecure Deserialization** | `pickle.loads(user_input)` | Nunca deserialices datos del usuario con `pickle`, `yaml.load()` sin `SafeLoader`, o `json` sin schema validation |
| **Broken Authentication** | Passwords en texto plano, sesiones sin expiración | Usa librerías probadas (bcrypt, argon2), JWT con expiración, HTTPS obligatorio |
| **Security Misconfiguration** | `DEBUG=True` en producción, headers por defecto | Desactiva debug, usa headers de seguridad (CSP, HSTS, X-Frame-Options), oculta versiones de stack |
| **Sensitive Data Exposure** | Enviar datos sensibles sin TLS, logs con passwords | HTTPS everywhere, enmascara datos en logs, cifra en reposo |

### OWASP Top 10 — Checklist por feature web

Antes de declarar `done` en una feature que expone una interfaz web o API:

- [ ] **A01: Broken Access Control** — Los endpoints validan autenticación y autorización. No se confía en `user_id` del request sin verificar ownership.
- [ ] **A02: Cryptographic Failures** — Contraseñhas hasheadas con bcrypt/argon2. Tokens JWT firmados y con expiración. HTTPS en producción.
- [ ] **A03: Injection** — Todas las queries a base de datos usan parametrización. No hay `f-string` SQL ni concatenación.
- [ ] **A04: Insecure Design** — Business logic validada server-side. No se confía en validación client-side.
- [ ] **A05: Security Misconfiguration** — `DEBUG=False`, headers de seguridad activos, versiones de dependencias actualizadas.
- [ ] **A06: Vulnerable and Outdated Components** — `security-check.py` dependency audit pasa sin CVEs críticas.
- [ ] **A07: Identification and Authentication Failures** — Rate limiting en login, bloqueo tras intentos fallidos, sesiones invalidadas en logout.
- [ ] **A08: Software and Data Integrity Failures** — Dependencias instaladas desde fuentes verificadas (PyPI, npm registry oficial). No se usa `pip install` desde URLs arbitrarias.
- [ ] **A09: Security Logging and Monitoring Failures** — Eventos de seguridad logueados (login fallido, acceso no autorizado). Logs no contienen secrets.
- [ ] **A10: Server-Side Request Forgery (SSRF)** — No se usan URLs proporcionadas por el usuario para hacer requests internos. Whitelist de dominios permitidos.

### Recomendaciones por stack

#### Python (Flask / FastAPI / Django)

- **SQLi:** Usa SQLAlchemy ORM o queries parametrizadas. Nunca concatenes strings.
- **XSS:** Flask usa Jinja2 con autoescaping por defecto. No uses `| safe` sin validar.
- **Deserialización:** Usa `yaml.safe_load()` en lugar de `yaml.load()`. Nunca uses `pickle` con datos del usuario.
- **Command injection:** Prefiere `subprocess.run([cmd, arg1, arg2])` sobre `subprocess.run(cmd, shell=True)`.
- **Dependency audit:** `pip install pip-audit && pip-audit`

#### Node.js (Express / NestJS)

- **SQLi:** Usa ORMs (Sequelize, Prisma, TypeORM) o queries parametrizadas.
- **XSS:** Escapa output con librerías como `escape-html` o usa templates seguros (EJS, Pug).
- **Eval:** Nunca uses `eval()` o `new Function()` con input del usuario.
- **Command injection:** Usa `child_process` con arrays, nunca con `shell: true` y input concatenado.
- **Dependency audit:** `npm audit` (incluido con npm)

#### Go

- **SQLi:** Usa `database/sql` con placeholders (`$1`, `$2`).
- **XSS:** Usa `html/template` en lugar de `text/template` para HTML.
- **Command injection:** `exec.Command()` con argumentos separados, nunca concatenados.
- **Dependency audit:** `go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...`

---

## Checklist de seguridad para nuevas features

- [ ] No se añaden secrets hardcodeados.
- [ ] No se ejecutan comandos con `sudo` o `rm -rf` sin confirmación.
- [ ] No se añaden dependencias sin justificar.
- [ ] `.gitignore` cubre nuevos archivos sensibles si se introducen.
- [ ] `security-check.py` pasa antes de declarar `done`.
- [ ] Se validan symlinks en archivos críticos si se añaden nuevos scripts del harness.
- [ ] Si es una aplicación web, se revisa el checklist OWASP Top 10.
