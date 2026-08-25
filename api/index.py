"""Vercel Serverless Function Entrypoint for FastAPI Backend.

Adds the backend package to the Python runtime path and exports
the primary FastAPI ASGI application instance.
"""

import os
import sys
from pathlib import Path

# Resolve paths: add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import initialized FastAPI application (backend resolved dynamically in sys.path)
try:
    from app.main import app  # type: ignore[import-not-found, import-untyped]  # pyright: ignore[reportMissingImports]
except ImportError:
    from backend.app.main import app  # type: ignore[import-not-found, import-untyped]  # pyright: ignore[reportMissingImports]

# Export app as handler
handler = app

