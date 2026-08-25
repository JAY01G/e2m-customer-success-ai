"""FastAPI root entrypoint alias for Vercel deployment.

Exports the initialized FastAPI app from app.main.
"""

from app.main import app

__all__ = ["app"]
