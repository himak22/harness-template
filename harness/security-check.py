#!/usr/bin/env python3
"""security-check.py — Verificación de seguridad automatizada.

Se ejecuta automáticamente desde start.py y done.py.
Puede ejecutarse manualmente: ./harness/security-check.py

Comprueba:
  1. Secrets hardcodeados en src/
  2. Archivos sensibles sin .gitignore
  3. Comandos peligrosos en scripts
  4. Datos PII en tests/fixtures
"""

import os
import re
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
    """Busca patrones de secrets hardcodeados en src/."""
    global SEVERITY
    patterns = [
        (r'api[_-]?key\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']', "Possible API key"),
        (r'secret\s*[:=]\s*["\'][a-zA-Z0-9]{8,}["\']', "Possible secret"),
        (r'password\s*[:=]\s*["\'][^"\']{4,}["\']', "Possible password"),
        (r'token\s*[:=]\s*["\'][a-zA-Z0-9._-]{20,}["\']', "Possible token"),
        (r'Bearer\s+[a-zA-Z0-9._-]{20,}', "Possible Bearer token"),
        (r'sk-[a-zA-Z0-9]{20,}', "Possible OpenAI/API key"),
        (r'AKIA[0-9A-Z]{16}', "Possible AWS access key"),
    ]

    found = False
    src_dir = "src"
    if not os.path.exists(src_dir):
        warn("No src/ directory found, skipping secret scan")
        return

    for root, _, files in os.walk(src_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
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

    if not found:
        ok("No hardcoded secrets detected in src/")


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
    dangerous = [
        (r'\brm\s+-rf\s+/', "Dangerous rm -rf detected"),
        (r'\bcurl\s+.*\|\s*(ba)?sh', "curl | bash pattern detected"),
        (r'\bwget\s+.*\|\s*(ba)?sh', "wget | bash pattern detected"),
        (r'\bsudo\b', "sudo command detected"),
    ]

    found = False
    script_extensions = (".sh", ".py", ".js", ".ts", ".go", ".rb")
    for root, _, files in os.walk("."):
        # Skip hidden dirs and common non-project dirs
        if any(part.startswith(".") for part in root.split(os.sep) if part):
            if ".git" in root or "node_modules" in root or "__pycache__" in root:
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
                if re.search(pattern, content, re.IGNORECASE):
                    # Exclude harness/ scripts (they're trusted)
                    if "harness/" in fpath:
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


def main():
    print("── Security Check ──────────────────────────────────────")

    check_secrets_in_source()
    check_sensitive_files_gitignored()
    check_dangerous_commands()
    check_pii_in_tests()

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
