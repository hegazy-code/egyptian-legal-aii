"""
Top-level test-suite path setup.

This is the whole-system tests/ directory (retrieval/legal_qa/security/
regression) -- distinct from backend/tests/, which unit-tests the FastAPI
app in isolation and has its own conftest.py.

A few of these tests (tests/security/) import backend application code
directly (e.g. app.rag.engine) to check prompt-construction behavior
without needing a running server or a real Gemini API key. To make `import
app...` work no matter what directory `pytest` is invoked from, add
backend/ to sys.path here.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
