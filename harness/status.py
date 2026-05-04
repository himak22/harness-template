#!/usr/bin/env python3
"""status.py — Briefing rápido del estado del proyecto.

Uso: ./harness/status.py

Muestra en 10 líneas todo lo que un agente necesita saber antes de trabajar.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Determinar directorio base del proyecto (padre de harness/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
os.chdir(BASE_DIR)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def ok(msg):
    print(f"{GREEN}[OK]{NC}    {msg}")


def fail(msg):
    print(f"{RED}[FAIL]{NC}  {msg}")


def warn(msg):
    print(f"{YELLOW}[WARN]{NC}  {msg}")


def info(msg):
    print(f"{BLUE}[INFO]{NC}  {msg}")


def load_features():
    with open("feature_list.json", "r", encoding="utf-8") as f:
        return json.load(f)


def check_init():
    result = subprocess.run(["./init.sh"], capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


def main():
    print("═" * 58)
    print("  HARNESS STATUS")
    print("═" * 58)

    # 1. Features
    try:
        data = load_features()
        features = data.get("features", [])
        in_progress = [f for f in features if f["status"] == "in_progress"]
        pending = [f for f in features if f["status"] == "pending"]
        done = [f for f in features if f["status"] == "done"]
        blocked = [f for f in features if f["status"] == "blocked"]

        info(f"Project: {data.get('project', 'unknown')}")
        print()

        if in_progress:
            f = in_progress[0]
            warn(f"IN PROGRESS: #{f['id']} {f['name']}")
            print(f"  Title: {f['title']}")
            print(f"  Desc:  {f['description'][:60]}...")
        else:
            ok("No session active")

        if pending:
            next_f = min(pending, key=lambda x: x["id"])
            info(f"Next up: #{next_f['id']} {next_f['name']}")
        else:
            info("No pending features")

        print(f"  Done: {len(done)} | Pending: {len(pending)} | Blocked: {len(blocked)}")
        print()

    except Exception as e:
        fail(f"Cannot read feature_list.json: {e}")
        sys.exit(1)

    # 2. init.sh status
    print("── init.sh ──────────────────────────────────────────────")
    is_green, output = check_init()
    if is_green:
        ok("All checks pass")
    else:
        fail("Some checks FAILED")
        # Show last failure line
        for line in output.splitlines():
            if "[FAIL]" in line or "Error" in line:
                print(f"  {line.strip()}")
                break
    print()

    # 3. Current session
    print("── progress/current.md ──────────────────────────────────")
    if os.path.exists("progress/current.md"):
        with open("progress/current.md", "r", encoding="utf-8") as f:
            content = f.read()
        if "Feature en curso: _ninguna_" in content or "Feature en curso: _—_" in content:
            ok("No active session")
        else:
            # Extract feature line
            for line in content.splitlines():
                if "Feature en curso:" in line:
                    print(f"  {line.strip()}")
                    break
    else:
        fail("Missing progress/current.md")
    print()

    # 4. Quick actions
    print("── Actions ──────────────────────────────────────────────")
    if in_progress:
        print("  ./harness/done.sh     → Finish current feature")
        print("  ./harness/block.sh    → Block current feature")
    else:
        print("  ./harness/start.sh    → Start next pending feature")
    print("═" * 58)


if __name__ == "__main__":
    main()
