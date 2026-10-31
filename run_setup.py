#!/usr/bin/env python3
"""
Egyptian Legal AI — one-shot setup and launch.
Run from the project root:  python run_setup.py
"""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BACKEND = ROOT / "backend"
PYTHON = sys.executable  # same python that is running this script


def run(cmd, cwd=None, check=True):
    print(f"\n>>> {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT, check=check)
    return result


print("=" * 50)
print("  Egyptian Legal AI — Setup and Launch")
print("=" * 50)

# 1. Install dependencies
print("\n[1/4] Installing backend dependencies...")
run([PYTHON, "-m", "pip", "install", "-r", str(BACKEND / "requirements.txt"), "-q"])
print("Done.")

# 2. Run migrations
print("\n[2/4] Running database migrations...")
run([PYTHON, "-m", "alembic", "upgrade", "head"], cwd=BACKEND)
print("Done.")

# 3. Seed law articles
print("\n[3/4] Seeding law articles...")
seed_script = ROOT / "scripts" / "seed_laws_direct.py"
run([PYTHON, str(seed_script), "--backend-dir", str(BACKEND)], cwd=ROOT)
print("Done.")

# 4. Start backend
print("\n[4/4] Starting backend on http://localhost:8000 ...")
print("      Press Ctrl+C to stop.\n")
subprocess.run(
    [PYTHON, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
    cwd=BACKEND,
)
