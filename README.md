# CodeGuru AI

> AI-powered full-stack coding mentor platform with concurrent code reviews, interactive DSA tutoring, and mock technical interviews.

---

## Overview

CodeGuru AI is a production-grade SaaS platform built to accelerate software engineering learning. It combines a multi-agent AI pipeline with a modern full-stack architecture to deliver real-time code reviews, step-through algorithm debugging, and scored mock interview sessions.

The platform routes developer intent automatically through a coordinator agent that delegates to specialized sub-agents (reviewer, debugger, teacher, interviewer), each powered by configurable LLM providers with offline fallback support.

---

## Features

- **AI Code Reviews** -- Submit code and receive parallel analysis covering bugs, complexity, style, and security vulnerabilities across multiple languages.
- **Interactive DSA Mentor** -- Trace algorithm executions line-by-line with variable state visualization and complexity breakdowns.
- **Mock Technical Interviews** -- Practice behavioral and coding interview scenarios with AI-driven scoring and detailed feedback.
- **Multi-Agent Orchestration** -- A coordinator agent detects developer intent and routes tasks to specialized agents automatically.
- **Analytics Dashboard** -- Track learning streaks, skill progression, and session history with interactive charts.
- **Document Management** -- Upload and index reference documents for retrieval-augmented generation (RAG) queries.
- **Custom API Key Support** -- Users can override AI provider keys via client-side settings for personal OpenAI/Ollama endpoints.
- **Subscription Tiers** -- Built-in free, pro, and team tiers with configurable rate limits and Stripe billing integration.
- **OAuth & JWT Auth** -- Google OAuth sign-in with secure refresh-token rotation and bcrypt password hashing.
- **Offline Fallback** -- Automatic routing to local Ollama models (e.g. `codellama`) when cloud API keys are absent.

---

## Tech Stack

### Backend

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115, Python 3.12 |
| ORM | SQLAlchemy 2.0 (async), Alembic |
| Database | PostgreSQL 16 (asyncpg) / SQLite (dev) |
| Cache | Redis 7.2 |
| Queue | Celery 5.4 |
| AI Providers | OpenAI, Google Gemini, Ollama |
| LLM Framework | LangChain 0.2, tiktoken |
| Code Analysis | tree-sitter, pylint, bandit, radon |
| Vector Store | ChromaDB, sentence-transformers |
| Billing | Stripe |
| Monitoring | Prometheus, Grafana |
| Auth | python-jose (JWT), passlib (bcrypt) |

### Frontend

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 15.3 (App Router), React 19 |
| Language | TypeScript 5.4 |
| Styling | Tailwind CSS 3.4 |
| State | Zustand 4.5, TanStack Query v5 |
| Editor | Monaco Editor |
| 3D / WebGL | React Three Fiber, Three.js |
| Animations | Framer Motion, GSAP |
| Forms | React Hook Form, Zod |
| Charts | Recharts |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| Containers | Docker, Docker Compose |
| Reverse Proxy | Nginx 1.25 |
| CI/CD | Makefile automation |

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (backend dependency manager)
- Docker & Docker Compose (optional, for database services)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/codeguru-ai.git
cd codeguru-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env
```

Edit `.env` with your credentials (see [Environment Variables](#environment-variables)).

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | JWT signing secret (min 32 chars) | `DEV_SECRET_KEY_PLACEHOLDER...` |
| `SQLALCHEMY_DATABASE_URI` | No | Full database connection string | Assembled from individual vars |
| `POSTGRES_SERVER` | No | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | No | PostgreSQL port | `5432` |
| `POSTGRES_USER` | No | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | No | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | No | PostgreSQL database name | `codeguru` |
| `REDIS_HOST` | No | Redis host | `localhost` |
| `REDIS_PORT` | No | Redis port | `6379` |
| `OPENAI_API_KEY` | No | OpenAI API key (skips to Ollama if unset) | -- |
| `OLLAMA_HOST` | No | Ollama server URL | `http://localhost:11434` |
| `GEMINI_API_KEY` | No | Google Gemini API key | -- |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID | -- |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret | -- |
| `STRIPE_SECRET_KEY` | No | Stripe secret key | -- |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook signing secret | -- |
| `ENVIRONMENT` | No | `development`, `staging`, or `production` | `development` |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | No | Backend API base URL | `/api/v1` |

---

## Running the Application

### Backend

```bash
cd backend

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Celery Worker (optional)

```bash
celery -A app.main worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Running Tests

```bash
cd backend
pytest
```

---

## Docker Setup

### Development (full stack)

```bash
# Start all services (PostgreSQL, Redis, backend, frontend, Nginx)
docker-compose up -d

# Run database migrations inside the backend container
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production

```bash
# Start with production config (includes Prometheus + Grafana)
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Makefile Shortcuts

```bash
make dev          # docker-compose up -d
make build        # docker-compose up --build -d
make down         # docker-compose down
make migrate      # Run alembic migrations
make test         # Run pytest suite
make logs         # Tail all container logs
make shell-backend   # Shell into backend container
make shell-frontend  # Shell into frontend container
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js application |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & Celery broker |
| Nginx | 80 | Reverse proxy |

---

## Screenshots

> Add screenshots or GIFs of the application below.

<!-- 
![Landing Page](docs/screenshots/landing.png)
![Dashboard](docs/screenshots/dashboard.png)
![Code Review](docs/screenshots/review.png)
![DSA Mentor](docs/screenshots/dsa.png)
![Mock Interview](docs/screenshots/interview.png)
![Analytics](docs/screenshots/analytics.png)
-->

---

## API Reference

Full API documentation is available at [`docs/API.md`](docs/API.md).

Key endpoint groups:

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/api/v1/auth` | Register, login, token refresh, OAuth |
| Users | `/api/v1/users` | Profile management |
| Reviews | `/api/v1/reviews` | Code review submissions & results |
| DSA | `/api/v1/dsa` | Algorithm tutoring sessions |
| Interview | `/api/v1/interview` | Mock interview sessions |
| Coordinator | `/api/v1/coordinator` | Multi-agent intent routing |
| Analytics | `/api/v1/analytics` | Learning metrics & dashboards |
| Billing | `/api/v1/billing` | Stripe subscription management |
| Documents | `/api/v1/chat` | RAG document upload & queries |
| Admin | `/api/v1/admin` | Administrative operations |

---

## Project Structure

```
codeguru-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # Multi-agent orchestration
│   │   ├── ai/              # LLM providers, routers, prompts
│   │   ├── api/v1/          # FastAPI route handlers
│   │   ├── core/            # Config, security, exceptions
│   │   ├── database/        # SQLAlchemy engine & sessions
│   │   ├── engine/          # Static code analysis pipeline
│   │   ├── middleware/       # Logging, rate limiting
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Data access layer
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── services/        # Business logic layer
│   ├── migrations/          # Alembic database migrations
│   ├── tests/               # Pytest test suite
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # UI, layout, Three.js components
│   │   ├── features/        # Feature-specific modules
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities, constants, configs
│   │   ├── schemas/         # Zod validation schemas
│   │   ├── services/        # Axios API service layer
│   │   ├── store/           # Zustand state stores
│   │   └── types/           # TypeScript type definitions
│   └── package.json         # Node.js dependencies
├── docker-compose.yml       # Development containers
├── docker-compose.prod.yml  # Production containers
├── nginx/                   # Reverse proxy config
├── monitoring/              # Prometheus & Grafana configs
└── docs/                    # API & deployment documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
