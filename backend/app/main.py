"""FastAPI Application Entrypoint.

Initializes the FastAPI application instance with rich Swagger/OpenAPI documentation,
lifespan lifecycle events, CORS middleware, global error handlers, and mounted API routers.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.config.logging import logger
from app.database.database import init_db
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import auth, customers, dashboard, health, insights, interactions, users

settings = get_settings()

API_DESCRIPTION = """
Enterprise-grade backend API providing automated AI meeting insights, customer health scoring (0–100), touchpoint interaction management, and RBAC governance.

---


### 🔑 Authentication Guide

All protected endpoints require a valid JWT Bearer access token:

1. **Obtain Token**: Send a `POST` request to `/api/v1/auth/login` with your credentials.
2. **Authorize in Swagger**: Click the green **Authorize 🔓** button at the top right of this page.
3. **Enter Token**: Paste your token in the `JWTBearer` field and click **Authorize**.
4. **Session Persistence**: Swagger UI is configured to persist your token across page reloads.

---

### 🛡️ Role-Based Access Control (RBAC)

The platform enforces strict role-based access control with three operational tiers:

| Role | Description | Key Permissions |
| :--- | :--- | :--- |
| **`ADMIN`** | System Administrator | Full access: user provisioning, customer/interaction CRUD & deletion, AI analysis. |
| **`CUSTOMER_SUCCESS_MANAGER`** | CSM Account Owner | Create/edit customers, log interactions, run AI intelligence, view executive metrics. |
| **`VIEWER`** | Read-Only Stakeholder | View dashboard summary, browse customer accounts and interaction history. |

---

### 🚀 Key Capabilities

- **Automated AI Intelligence**: Extract executive summaries, sentiment classification (*Positive*, *Neutral*, *Negative*), action items, and risk factors from raw meeting notes.
- **Dynamic Customer Health Scoring**: Automated 0–100 health metrics with categorized risk tiers (*Healthy*, *Moderate*, *Critical*).
- **Redis High-Speed Caching**: Query caching with automatic cache invalidation on write mutations.
- **Observability & Probes**: Standard container liveness (`/health`) and dependency readiness (`/ready`) endpoints.
"""

OPENAPI_TAGS: List[Dict[str, Any]] = [
    {
        "name": "Authentication",
        "description": (
            "User authentication, registration, JWT token generation, token refresh (via HttpOnly cookie or header), "
            "and active profile inspection (`/me`)."
        ),
    },
    {
        "name": "Dashboard",
        "description": (
            "Consolidated executive metrics and telemetry: aggregate statistics, customer health score distributions, "
            "AI meeting sentiment breakdown, and prioritized at-risk retention queues."
        ),
    },
    {
        "name": "Customers",
        "description": (
            "Customer account lifecycle management: comprehensive filtering, multi-field search, health scoring (0-100), "
            "CSM owner assignment, and automated Redis caching."
        ),
    },
    {
        "name": "Interactions",
        "description": (
            "Customer communication touchpoints (Meetings, Calls, Emails, Demos). Includes meeting notes logging, "
            "duration tracking, and automated AI insight extraction triggering."
        ),
    },
    {
        "name": "AI Insights",
        "description": (
            "On-demand AI intelligence pipeline: automated executive summary synthesis, sentiment classification "
            "(Positive, Neutral, Negative), action item extraction, and risk detection."
        ),
    },
    {
        "name": "Users",
        "description": (
            "User administration and RBAC governance (Admin only): operator account provisioning, role updates "
            "(ADMIN, CUSTOMER_SUCCESS_MANAGER, VIEWER), and account status control."
        ),
    },
    {
        "name": "Health",
        "description": (
            "System diagnostics and container orchestration probes: `/health` (Liveness) and `/ready` (PostgreSQL and Redis readiness)."
        ),
    },
    {
        "name": "Root",
        "description": "Root service operational status and API documentation navigation links.",
    },
]

SWAGGER_UI_PARAMETERS: Dict[str, Any] = {
    "persistAuthorization": True,
    "docExpansion": "list",
    "filter": True,
    "showCommonExtensions": True,
    "syntaxHighlight.theme": "monokai",
    "tryItOutEnabled": True,
    "displayRequestDuration": True,
    "defaultModelsExpandDepth": 2,
    "defaultModelExpandDepth": 2,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager for FastAPI.

    Handles startup tasks (such as initializing database tables) and shutdown cleanup.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] environment...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=API_DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
    contact={
        "name": "Customer Success Platform API Support",
        "url": "https://localhost:3000",
    },
    license_info={
        "name": "MIT License",
        "identifier": "MIT",
    },
    lifespan=lifespan,
)

# Request Logging Middleware
app.add_middleware(RequestLoggerMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Register API Routers
api_v1_prefix = settings.API_V1_PREFIX
app.include_router(health.router)  # /health & /ready at root
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(users.router, prefix=api_v1_prefix)
app.include_router(customers.router, prefix=api_v1_prefix)
app.include_router(interactions.router, prefix=api_v1_prefix)
app.include_router(insights.router, prefix=api_v1_prefix)
app.include_router(dashboard.router, prefix=api_v1_prefix)


@app.get(
    "/",
    tags=["Root"],
    summary="Get service operational metadata",
    response_description="Basic application metadata and documentation URLs",
)
def root() -> Dict[str, Any]:
    """Root metadata endpoint returning service name, status, and API documentation link.

    Returns:
        Dict[str, Any]: Basic application health and operational metadata.
    """
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/api/v1/openapi.json",
        "status": "operational",
    }


# Export ASGI handler alias for Vercel Serverless Function compatibility
handler = app



