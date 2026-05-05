# Configuración de CI/CD

> Este documento explica cómo usar y extender el workflow de GitHub Actions incluido en este template.

## Qué incluye el template

El archivo `.github/workflows/ci.yml` se copia automáticamente cuando alguien usa este repositorio como template. Verifica que el arnés está sano en cada PR y push a `main`:

1. **`init.sh`** — Valida la estructura del proyecto, archivos base del arnés, entorno y tests.
2. **`security-check.py`** — Detecta secrets hardcodeados, comandos peligrosos, vulnerabilidades SAST básicas, CVEs en dependencias y leaks en historial git.
3. **Validación de `feature_list.json`** — Rechaza PRs con features bloqueadas o más de una feature en progreso.
4. **Permisos de scripts** — Verifica que todos los scripts del harness sean ejecutables.
5. **Sesiones stale** — Advierte si `progress/current.md` contiene una sesión no vaciada.

## Cómo extender CI para tu proyecto

El workflow del arnés solo verifica el arnés. **Debes añadir tus propios jobs para verificar el código de tu proyecto.**

### Ejemplo: Proyecto Python (FastAPI/Django/Flask)

Añade esto al final de `.github/workflows/ci.yml`:

```yaml
  project-tests:
    runs-on: ubuntu-latest
    name: Run Project Tests
    needs: harness-checks
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ -v --cov=src --cov-report=term-missing
```

### Ejemplo: Proyecto Node.js (React/Express/NestJS)

```yaml
  project-tests:
    runs-on: ubuntu-latest
    name: Run Project Tests
    needs: harness-checks
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm ci
      - name: Run linter
        run: npm run lint
      - name: Run tests
        run: npm test
```

### Ejemplo: Proyecto Go

```yaml
  project-tests:
    runs-on: ubuntu-latest
    name: Run Project Tests
    needs: harness-checks
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Download dependencies
        run: go mod download
      - name: Run tests
        run: go test ./... -v -race
      - name: Run security scan
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...
```

### Ejemplo: Proyecto Rust

```yaml
  project-tests:
    runs-on: ubuntu-latest
    name: Run Project Tests
    needs: harness-checks
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rust-lang/setup-rust-toolchain@v1
      - name: Run tests
        run: cargo test --all-features
      - name: Run clippy
        run: cargo clippy -- -D warnings
      - name: Run audit
        run: |
          cargo install cargo-audit
          cargo audit
```

## Buenas prácticas

1. **Separa los jobs.** El job `harness-checks` verifica el arnés. El job `project-tests` verifica tu código. Usa `needs: harness-checks` para que los tests del proyecto solo corran si el arnés está sano.
2. **No modifiques los steps del arnés.** Si necesitas personalizar el workflow del arnés, hazlo en el repo del template, no en cada proyecto derivado.
3. **Añade coverage.** Usa `pytest-cov` (Python), `nyc` (Node), `go test -cover` (Go) para reportar cobertura.
4. **Protege la rama main.** En GitHub, ve a Settings > Branches > Add rule:
   - Require pull request reviews before merging.
   - Require status checks to pass before merging (selecciona `Harness CI / Verify Harness Engineering Template`).
5. **Cachea dependencias.** Usa `actions/cache` para acelerar builds (especialmente `node_modules/` y `~/.cargo/registry`).

## Desactivar CI del arnés

Si el workflow del arnés te molesta en un proyecto concreto (por ejemplo, un fork experimental), puedes desactivarlo:

```bash
rm .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "ci: remove harness workflow for experimental fork"
```

Pero piénsalo dos veces: el arnés te protege de mergear código roto o con secrets filtrados.

## Troubleshooting

### `init.sh` falla en CI pero pasa localmente

- Verifica que `python3` esté disponible en el runner (usamos `actions/setup-python@v5`).
- Algunos runners de GitHub no tienen `go` o `cargo` instalados por defecto. Instálalos explícitamente si tu stack los necesita.

### `security-check.py` detecta falsos positivos

- Revisa la sección "Qué NO detecta security-check.py" en `docs/security.md`.
- Los checks SAST y dependency audit son WARN-only. No bloquean el merge.
- Si un check crítico (secrets, comandos peligrosos) da falso positivo, documenta la excepción en `progress/current.md` y abre una issue.

### El workflow no se ejecuta

- Verifica que el archivo esté en `.github/workflows/ci.yml` (la carpeta `.github` debe existir en la raíz).
- Verifica que los triggers (`on: push/pull_request`) incluyan la rama correcta (`main` o `master`).
