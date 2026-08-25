"""Vercel Serverless Function Entrypoint for Backend Service.

Exports the primary FastAPI ASGI application instance for Vercel deployment.
"""

from app.main import app

# Export app as handler for Vercel Serverless Functions
handler = app
