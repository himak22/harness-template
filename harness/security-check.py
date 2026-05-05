#!/usr/bin/env python3
"""security-check.py — Verificación de seguridad automatizada.

Se ejecuta automáticamente desde start.py y done.py.
Puede ejecutarse manualmente: ./harness/security-check.py

Comprueba:
  1. Secrets hardcodeados en src/, config/, scripts/
  2. Archivos sensibles sin .gitignore
  3. Comandos peligrosos en scripts
  4. Datos PII en tests/fixtures
  5. Vulnerabilidades de aplicación (SAST básico: SQLi, XSS, command injection)
  6. Vulnerabilidades en dependencias (CVEs por stack)
  7. Leaks de secrets en historial de git

Nota: Los checks 5, 6 y 7 son informativos (WARN) y no bloquean el cierre.
"""

import os
import re
import subprocess
import sys

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"


def ok(msg): print(f"{GREEN}[OK]{NC}    {msg}")
def fail(msg): print(f"{RED}[FAIL]{NC}  {msg}")
def warn(msg): print(f"{YELLOW}[WARN]{NC}  {msg}")


# Determinar directorio base del proyecto (padre de harness/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
os.chdir(BASE_DIR)

SEVERITY = "PASS"  # PASS, WARN, FAIL


def check_secrets_in_source():
    """Busca patrones de secrets hardcodeados en src/, config/, scripts/, .github/ y archivos de configuracion."""
    global SEVERITY
    patterns = [
        (r'api[_-]?key\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']', "Possible API key"),
        (r'secret\s*[:=]\s*["\'][a-zA-Z0-9]{8,}["\']', "Possible secret"),
        (r'password\s*[:=]\s*["\'][^"\']{4,}["\']', "Possible password"),
        (r'token\s*[:=]\s*["\'][a-zA-Z0-9._-]{20,}["\']', "Possible token"),
        (r'Bearer\s+[a-zA-Z0-9._-]{20,}', "Possible Bearer token"),
        (r'sk-[a-zA-Z0-9]{20,}', "Possible OpenAI/API key"),
        (r'AKIA[0-9A-Z]{16}', "Possible AWS access key"),
        (r'ghp_[a-zA-Z0-9]{36}', "Possible GitHub personal access token"),
        (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', "Possible GitHub fine-grained PAT"),
        (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', "Possible JWT token"),
        (r'postgres(ql)?://[^:]+:[^@]+@', "Possible database URI with password"),
        (r'mysql://[^:]+:[^@]+@', "Possible MySQL URI with password"),
        (r'mongodb(\+srv)?://[^:]+:[^@]+@', "Possible MongoDB URI with password"),
        (r'private[_-]?key\s*[:=]\s*["\'][^"\']{20,}["\']', "Possible private key"),
    ]

    any_found = False
    scan_dirs = ["src", "config", "scripts", ".github"]
    config_files = ["docker-compose.yml", "docker-compose.yaml", "Dockerfile", ".env.example"]
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".tox"}

    # Scan directories
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        for root, _, files in os.walk(scan_dir):
            if any(skip in root for skip in skip_dirs):
                continue
            for fname in files:
                fpath = os.path.join(root, fname)
                if _scan_file_for_secrets(fpath, patterns):
                    any_found = True

    # Scan individual config files
    for cf in config_files:
        if os.path.exists(cf):
            if _scan_file_for_secrets(cf, patterns):
                any_found = True

    if not any_found:
        ok("No hardcoded secrets detected")
    if not any(os.path.exists(d) for d in scan_dirs):
        warn("No source/config directories found, secret scan limited")


def _scan_file_for_secrets(fpath, patterns):
    """Helper to scan a single file for secret patterns. Returns True if secrets found."""
    global SEVERITY
    found = False
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False
    for pattern, desc in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for m in matches:
            # Skip dummy/test values
            val = m.group(0).lower()
            if any(x in val for x in ["example", "dummy", "test", "fake", "placeholder", "your_"]):
                continue
            fail(f"{desc} in {fpath}: {m.group(0)[:40]}...")
            found = True
            SEVERITY = "FAIL"
    return found


def check_sensitive_files_gitignored():
    """Verifica que archivos sensibles estén en .gitignore."""
    global SEVERITY
    sensitive_patterns = [
        ".env", ".env.local", ".env.production",
        "credentials.json", "secrets.json",
        "*.pem", "*.key", "*.p12", "*.pfx",
        "id_rsa", "id_ed25519", ".ssh/",
    ]

    gitignore_path = ".gitignore"
    if not os.path.exists(gitignore_path):
        fail("No .gitignore found!")
        SEVERITY = "FAIL"
        return

    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore = f.read()

    missing = []
    for pattern in sensitive_patterns:
        if pattern not in gitignore:
            missing.append(pattern)

    if missing:
        warn(f"Sensitive patterns not in .gitignore: {', '.join(missing[:3])}")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"
    else:
        ok("Sensitive files covered by .gitignore")


def check_dangerous_commands():
    """Busca comandos peligrosos en scripts del proyecto."""
    global SEVERITY
    # Patterns and descriptions are crafted to avoid self-detection in this file
    dangerous = [
        (r'\brm\s+-rf\s+/', "Dangerous rm -rf detected"),
        (r'\bc' + r'url\s+.*\|\s*(ba)?sh', "piping network fetch to shell detected"),
        (r'\bw' + r'get\s+.*\|\s*(ba)?sh', "piping w-get to shell detected"),
        (r'\bs' + r'udo\b', "privilege escalation command detected"),
    ]

    found = False
    script_extensions = (".sh", ".py", ".js", ".ts", ".go", ".rb")
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".tox"}
    for root, _, files in os.walk("."):
        # Skip hidden dirs and common non-project dirs
        if any(part.startswith(".") for part in root.split(os.sep) if part):
            if any(skip in root for skip in skip_dirs):
                continue
        for fname in files:
            if not fname.endswith(script_extensions):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
            for pattern, desc in dangerous:
                for m in re.finditer(pattern, content, re.IGNORECASE):
                    # Get the line containing the match to avoid self-detection
                    line_start = content.rfind('\n', 0, m.start()) + 1
                    line_end = content.find('\n', m.end())
                    if line_end == -1:
                        line_end = len(content)
                    line = content[line_start:line_end]
                    # Skip if this line is part of the dangerous patterns definition
                    if desc in line:
                        continue
                    fail(f"{desc} in {fpath}")
                    found = True
                    SEVERITY = "FAIL"

    if not found:
        ok("No dangerous commands in project scripts")


def check_pii_in_tests():
    """Busca datos PII reales en tests."""
    global SEVERITY
    pii_patterns = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "Possible real email"),
    ]

    found = False
    tests_dir = "tests"
    if not os.path.exists(tests_dir):
        warn("No tests/ directory found, skipping PII scan")
        return

    for root, _, files in os.walk(tests_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
            for pattern, desc in pii_patterns:
                matches = re.finditer(pattern, content)
                for m in matches:
                    email = m.group(0)
                    # Allow example/test emails
                    if any(x in email.lower() for x in ["example.com", "test.com", "dummy.com", "localhost"]):
                        continue
                    fail(f"{desc} in {fpath}: {email}")
                    found = True
                    SEVERITY = "FAIL"

    if not found:
        ok("No real PII detected in tests")


def _detect_stack():
    """Detecta el stack del proyecto igual que init.sh."""
    if os.path.exists("go.mod"):
        return "go"
    if os.path.exists("package.json"):
        return "node"
    if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml") or os.path.exists("src"):
        return "python"
    if os.path.exists("Cargo.toml"):
        return "rust"
    return "unknown"


def check_sast_vulnerabilities():
    """SAST básico: busca patrones de SQLi, XSS, command injection en código fuente.
    Este check es informativo (WARN) para no bloquear proyectos no-web."""
    global SEVERITY
    stack = _detect_stack()
    if stack == "unknown":
        warn("Stack no detectado, saltando SAST")
        return

    # Patrones por stack
    sast_patterns = {
        "python": [
            (r'\.execute\s*\(\s*["\'].*\%s.*["\']', "Possible SQL injection (string formatting in query)"),
            (r'\.execute\s*\(\s*f["\']', "Possible SQL injection (f-string in query)"),
            (r'os\.system\s*\(', "Possible command injection (os.system)"),
            (r'subprocess\.call\s*\(\s*[^\)]*shell\s*=\s*True', "Possible command injection (subprocess with shell=True)"),
            (r'render_template_string\s*\(', "Possible XSS (render_template_string with user input)"),
            (r'Markup\s*\(', "Possible XSS (Markup without escaping)"),
            (r'pickle\.loads?\s*\(', "Insecure deserialization (pickle)"),
            (r'yaml\.load\s*\([^,)]*\)', "Insecure deserialization (yaml.load without Loader)"),
        ],
        "node": [
            (r'\.query\s*\(\s*[`"\'].*\$\{.*\}[`"\']', "Possible SQL injection (template literal in query)"),
            (r'exec\s*\(', "Possible command injection (exec)"),
            (r'child_process', "Possible command injection (child_process)"),
            (r'innerHTML\s*=\s*[^;]+', "Possible XSS (innerHTML assignment)"),
            (r'document\.write\s*\(', "Possible XSS (document.write)"),
            (r'eval\s*\(', "Dangerous eval() detected"),
        ],
        "go": [
            (r'\.Query\s*\(\s*[^)]+\+', "Possible SQL injection (string concatenation in query)"),
            (r'fmt\.Sprintf\s*\([^,]*,.*\).*\.Query', "Possible SQL injection (Sprintf in query)"),
            (r'os\.Exec\s*\(', "Possible command injection (os.Exec with dynamic input)"),
            (r'template\.HTML\s*\(', "Possible XSS (template.HTML)"),
        ],
        "rust": [
            (r'\.query\s*\(\s*[^)]+format!', "Possible SQL injection (format! in query)"),
            (r'Command::new\s*\([^)]+format!', "Possible command injection (format! in Command)"),
        ],
    }

    patterns = sast_patterns.get(stack, [])
    if not patterns:
        warn(f"SAST no implementado para stack: {stack}")
        return

    extensions = {
        "python": ".py", "node": (".js", ".ts", ".jsx", ".tsx"),
        "go": ".go", "rust": ".rs"
    }
    ext = extensions.get(stack)

    found = False
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".tox", "target", "dist", "build"}
    for root, _, files in os.walk("."):
        if any(skip in root for skip in skip_dirs):
            continue
        for fname in files:
            if ext and not fname.endswith(ext):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
            for pattern, desc in patterns:
                for m in re.finditer(pattern, content, re.IGNORECASE):
                    line_start = content.rfind('\n', 0, m.start()) + 1
                    line_end = content.find('\n', m.end())
                    if line_end == -1:
                        line_end = len(content)
                    line = content[line_start:line_end].strip()
                    # Skip if this line is a comment explaining the pattern
                    if line.startswith("#") or line.startswith("//") or line.startswith("*"):
                        continue
                    warn(f"{desc} in {fpath}")
                    found = True
                    if SEVERITY != "FAIL":
                        SEVERITY = "WARN"

    if not found:
        ok(f"No SAST warnings for {stack} stack")


def check_dependency_vulnerabilities():
    """Intenta ejecutar herramientas nativas de dependency audit por stack.
    Es informativo (WARN) para no bloquear si la herramienta no está."""
    global SEVERITY
    stack = _detect_stack()

    if stack == "python":
        if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
            _run_tool("pip-audit", ["pip-audit", "--format=summary"], "Python dependency audit")
    elif stack == "node":
        if os.path.exists("package.json"):
            _run_tool("npm audit", ["npm", "audit", "--audit-level=moderate"], "Node dependency audit")
    elif stack == "go":
        if os.path.exists("go.mod"):
            _run_tool("govulncheck", ["govulncheck", "./..."], "Go vulnerability check")
    elif stack == "rust":
        if os.path.exists("Cargo.toml"):
            _run_tool("cargo audit", ["cargo", "audit"], "Rust dependency audit")
    else:
        warn("Dependency audit skipped (stack not detected or not supported)")


def _run_tool(name, cmd, desc):
    """Ejecuta una herramienta de dependency audit. WARN si falla o encuentra issues."""
    global SEVERITY
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            # npm audit retorna 1 si encuentra vulnerabilidades
            if "npm" in cmd and "audit" in cmd:
                warn(f"{desc}: vulnerabilities found. Run 'npm audit fix'.")
            elif "govulncheck" in cmd:
                warn(f"{desc}: vulnerabilities found.")
            elif "cargo" in cmd and "audit" in cmd:
                warn(f"{desc}: vulnerabilities found.")
            elif "pip-audit" in cmd:
                warn(f"{desc}: vulnerabilities found.")
            else:
                warn(f"{desc}: exited with code {result.returncode}")
            if SEVERITY != "FAIL":
                SEVERITY = "WARN"
        else:
            ok(f"{desc}: no known vulnerabilities")
    except FileNotFoundError:
        warn(f"{desc}: tool '{name}' not installed. Install it for CVE scanning.")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"
    except subprocess.TimeoutExpired:
        warn(f"{desc}: timed out after 120s")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"
    except Exception as e:
        warn(f"{desc}: error running tool: {e}")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"


def check_git_history_leaks():
    """Escanea el historial de git buscando leaks de secrets.
    Es informativo (WARN) para no bloquear repos con historial previo."""
    global SEVERITY
    if not os.path.exists(".git"):
        warn("Not a git repository, skipping git history scan")
        return

    # Patterns to search in git history
    history_patterns = [
        (r'AKIA[0-9A-Z]{16}', "Possible AWS access key in git history"),
        (r'ghp_[a-zA-Z0-9]{36}', "Possible GitHub PAT in git history"),
        (r'sk-[a-zA-Z0-9]{20,}', "Possible OpenAI/API key in git history"),
        (r'api[_-]?key\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']', "Possible API key in git history"),
        (r'password\s*[:=]\s*["\'][^"\']{4,}["\']', "Possible password in git history"),
    ]

    found = False
    try:
        # Scan last 100 commits with patches
        result = subprocess.run(
            ["git", "log", "-100", "-p", "--all"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            warn("Could not scan git history")
            if SEVERITY != "FAIL":
                SEVERITY = "WARN"
            return

        for pattern, desc in history_patterns:
            matches = re.finditer(pattern, result.stdout, re.IGNORECASE)
            for m in matches:
                val = m.group(0).lower()
                if any(x in val for x in ["example", "dummy", "test", "fake", "placeholder", "your_"]):
                    continue
                warn(f"{desc}: {m.group(0)[:40]}...")
                found = True
                if SEVERITY != "FAIL":
                    SEVERITY = "WARN"

        if not found:
            ok("No obvious secrets in recent git history (last 100 commits)")
    except subprocess.TimeoutExpired:
        warn("Git history scan timed out")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"
    except Exception as e:
        warn(f"Git history scan error: {e}")
        if SEVERITY != "FAIL":
            SEVERITY = "WARN"


def main():
    print("── Security Check ──────────────────────────────────────")

    # Checks críticos (pueden causar FAIL)
    check_secrets_in_source()
    check_sensitive_files_gitignored()
    check_dangerous_commands()
    check_pii_in_tests()

    # Checks informativos (solo WARN, nunca FAIL)
    print()
    print("── Application Security (SAST) ─────────────────────────")
    check_sast_vulnerabilities()

    print()
    print("── Dependency Audit (CVEs) ─────────────────────────────")
    check_dependency_vulnerabilities()

    print()
    print("── Git History Scan ────────────────────────────────────")
    check_git_history_leaks()

    print()
    if SEVERITY == "PASS":
        ok("Security check passed")
        sys.exit(0)
    elif SEVERITY == "WARN":
        warn("Security check completed with warnings")
        sys.exit(0)
    else:
        fail("Security check FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
