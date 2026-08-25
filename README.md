# AI-Powered Customer Success Platform

An enterprise-grade Customer Success Platform featuring automated meeting analysis, AI sentiment scoring, risk & action item extraction, customer health scoring, role-based access control (RBAC), and active Redis cache invalidation.

---

## 1. Project Overview

The **AI-Powered Customer Success Platform** enables Customer Success teams to manage client lifecycles, log interaction notes, and automatically derive actionable intelligence. Powered by an AI provider pipeline, the system extracts executive summaries, sentiment ratings, customer blockers, and follow-up items while persisting telemetry into a normalized PostgreSQL database and caching read-heavy endpoints in Redis.

---

## 2. Key Features

* **AI Meeting Intelligence**: Automatically analyzes meeting transcripts/notes to extract sentiment (`Positive`, `Neutral`, `Negative`), action items, and account risks with strict Pydantic schema validation.
* **Resilient AI Pipeline**: Provider abstraction supporting OpenAI, Anthropic, and offline deterministic Mock providers with automatic retry, timeout protection, and heuristic fallbacks.
* **Customer Portfolio Health**: Health scoring (0–100) with visual telemetry gauges and multi-status account tracking (`ACTIVE`, `AT_RISK`, `PROSPECT`, `CHURNED`).
* **Role-Based Access Control (RBAC)**: Backend-enforced role policies for `ADMIN`, `CUSTOMER_SUCCESS_MANAGER`, and `VIEWER`.
* **High-Performance Redis Caching**: Active cache population and instant cache invalidation upon any customer or interaction mutation. Graceful degradation if Redis is offline.
* **Clean MVC Backend**: Strict separation across Routers, Controllers, Services, Repositories, Schemas, and Models in FastAPI.
* **Modern Next.js App Router UI**: Next.js 15/16 with TypeScript, Redux Toolkit, React Hook Form, Zod validation, and dark glassmorphic SaaS design.
* **Containerized Deployment**: Multi-stage production `Dockerfile`s and `docker-compose.yml` with health checks, persistent volumes, and isolated networks.

---

## 3. Technology Stack

### Backend
* **Language & Runtime**: Python 3.11+ / Python 3.14 compatible
* **Web Framework**: FastAPI 0.115.x
* **ORM & Migrations**: SQLAlchemy 2.0.x & Alembic
* **Validation**: Pydantic v2
* **Database**: PostgreSQL 16 (or SQLite for isolated testing)
* **Caching**: Redis 7
* **Authentication**: JWT (PyJWT) + Argon2id (passlib)
* **Testing**: Pytest & Pytest-Asyncio
* **HTTP Client**: HTTPX

### Frontend
* **Framework**: Next.js 15.1.x / 16.x App Router
* **Language**: TypeScript (Strict Mode)
* **State Management**: Redux Toolkit & React-Redux
* **Form Validation**: React Hook Form + Zod
* **Icons**: Lucide React
* **Styling**: Vanilla CSS Variables & Design Tokens (Dark Glassmorphism)
* **Testing**: Vitest, React Testing Library, jsdom

---

## 4. Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── config/              # Application settings & structured logging
│   │   ├── database/            # SQLAlchemy engine, base & session dependencies
│   │   ├── models/              # User, Customer, Interaction, AIInsight models
│   │   ├── schemas/             # Pydantic v2 request & response schemas
│   │   ├── repositories/        # Database query encapsulation layer
│   │   ├── services/            # Business logic, AI engine & Redis cache
│   │   ├── controllers/         # HTTP request orchestration
│   │   ├── routers/             # API v1 route definitions
│   │   ├── dependencies/        # JWT auth & RBAC permission dependencies
│   │   ├── middleware/          # Centralized exception handler
│   │   ├── utils/               # Password hashing, JWT token & pagination utilities
│   │   ├── exceptions/          # Domain custom exceptions
│   │   └── main.py              # FastAPI application entrypoint
│   ├── alembic/                 # Migration environment and version scripts
│   ├── scripts/                 # Seed data script
│   ├── tests/                   # Unit and integration test suites
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   ├── customers/
│   │   ├── interactions/
│   │   ├── profile/
│   │   └── layout.tsx
│   ├── components/              # UI primitives, layout & domain widgets
│   ├── store/                   # Redux Toolkit store & feature slices
│   ├── services/                # Centralized Axios API client
│   ├── schemas/                 # Client Zod validation schemas
│   ├── types/                   # TypeScript interfaces
│   ├── tests/                   # Vitest & RTL test suites
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md
└── DATABASE_DIAGRAM.md
```

---

## 5. Prerequisites

* **Node.js**: v20.x or later
* **Python**: v3.11+ or v3.14.x
* **Docker & Docker Compose**: v2.20+ (for containerized execution)
* **PostgreSQL & Redis** (optional for manual local dev, included in Docker)

---

## 6. Environment Configuration

Copy the example environment configuration:
```bash
cp .env.example .env
```

### Key Environment Variables:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/customer_success_db

# Redis Caching
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=60
CACHE_ENABLED=true

# Security
JWT_SECRET=super-secret-jwt-key-change-in-production-min-32-chars-long!
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Configuration (mock, openai, or anthropic)
AI_PROVIDER=mock
AI_API_KEY=
AI_MODEL=gpt-4o-mini
AI_TIMEOUT=15
AI_TEMPERATURE=0.2

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 7. Running with Docker Compose (Recommended)

To start the entire application (PostgreSQL, Redis, FastAPI backend, and Next.js frontend):

```bash
docker compose up --build
```

### Verified Endpoints:
* **Frontend Application**: `http://localhost:3000`
* **Backend API & Swagger Docs**: `http://localhost:8000/docs`
* **ReDoc API Documentation**: `http://localhost:8000/redoc`
* **Liveness Health Check**: `http://localhost:8000/health`
* **Readiness Probe**: `http://localhost:8000/ready`

---

## 8. Local Development Setup (Manual)

### 8.1 Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Seed initial demo data:
   ```bash
   python scripts/seed_data.py
   ```
6. Start the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 8.2 Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000` in your browser.

---

## 9. Seed Data & Demo Credentials

When running `python scripts/seed_data.py`, the following demo accounts are created:

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin@example.com` | `Password123!` | Full permissions (User Management, Customer & Interaction CRUD, Deletions) |
| **CSM** | `csm@example.com` | `Password123!` | Customer Create/Update/Read, Log Meetings, Generate AI Insights |
| **Viewer** | `viewer@example.com` | `Password123!` | Read-only access to Dashboard, Customers, and Interactions |

*Tip: The login page includes 1-click quick-fill buttons for each demo account.*

---

## 10. Automated Testing

### 10.1 Running Backend Tests (Pytest)
The backend test suite includes 43 unit and integration tests covering authentication, RBAC authorization, customer CRUD, interaction workflows, AI parsing/fallbacks, and Redis caching.

```bash
cd backend
pytest -v
```

### 10.2 Running Frontend Tests (Vitest & RTL)
The frontend test suite validates login/register form validation, customer table gauges, AI insight cards, and dashboard metrics.

```bash
cd frontend
npm test
```

### 10.3 TypeScript Typecheck & Linting
```bash
cd frontend
npm run typecheck
npm run lint
```

### 10.4 Production Build Verification
```bash
cd frontend
npm run build
```

---

## 11. API Summary

| Method | Endpoint | Description | Access Role |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user | Public |
| `POST` | `/api/v1/auth/login` | Authenticate and receive JWT | Public |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Public (Cookie) |
| `GET` | `/api/v1/auth/me` | Current user profile | Authenticated |
| `GET` | `/api/v1/users` | List users | Admin |
| `GET` | `/api/v1/customers` | Paginated customer list with filters | Authenticated |
| `POST` | `/api/v1/customers` | Create customer account | CSM, Admin |
| `GET` | `/api/v1/customers/{id}` | Customer account details | Authenticated |
| `PATCH` | `/api/v1/customers/{id}` | Update customer details | CSM, Admin |
| `DELETE` | `/api/v1/customers/{id}` | Delete customer account | Admin |
| `GET` | `/api/v1/interactions` | Paginated interaction meeting logs | Authenticated |
| `POST` | `/api/v1/interactions` | Log meeting + auto AI insight trigger | CSM, Admin |
| `GET` | `/api/v1/interactions/{id}` | Interaction details | Authenticated |
| `PATCH` | `/api/v1/interactions/{id}` | Update meeting notes | CSM, Admin |
| `DELETE` | `/api/v1/interactions/{id}` | Delete interaction | Admin |
| `POST` | `/api/v1/interactions/{id}/insights` | Generate or regenerate AI insight | CSM, Admin |
| `GET` | `/api/v1/interactions/{id}/insights` | Retrieve AI insight | Authenticated |
| `GET` | `/api/v1/dashboard/summary` | Aggregated executive metrics & charts | Authenticated |
| `GET` | `/health` | Liveness check | Public |
| `GET` | `/ready` | Database & Redis readiness probe | Public |

---

## 12. AI Provider Architecture & Fallbacks

* **Provider Abstraction**: Defined under `app/services/ai_provider.py` with an abstract base class `AIProvider` and concrete implementations (`OpenAIProvider`, `AnthropicProvider`, `MockAIProvider`).
* **Validation**: Responses are stripped of markdown formatting and strictly validated using Pydantic v2 `AIInsightSchema`.
* **Fallback Behavior**: In the event of provider timeouts or malformed outputs, the system triggers automated retries and falls back to a deterministic heuristic insight with `generation_status = "FALLBACK"` without disrupting user workflows.

---

## 13. Redis Caching Strategy

* **Keys**:
  * `customers:list:{filters_hash}`
  * `customers:detail:{customer_id}`
  * `dashboard:summary`
* **TTL**: Configurable (default 60 seconds).
* **Active Invalidation**: Every customer create, update, or delete purges list and dashboard caches immediately.
* **Fault Tolerance**: If Redis is offline, the cache layer logs a warning and queries PostgreSQL directly without throwing 500 errors.

---

## 14. Architecture & Database Documentation

* [ARCHITECTURE.md](ARCHITECTURE.md) &mdash; Detailed MVC layer breakdown, request lifecycles, and Mermaid sequence diagrams.
* [DATABASE_DIAGRAM.md](DATABASE_DIAGRAM.md) &mdash; Normalized PostgreSQL schema, UUID primary keys, check constraints, indexes, and Mermaid ER diagram.
