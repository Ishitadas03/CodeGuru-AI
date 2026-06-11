# CodeGuru AI Production Deployment Guide

This document provides guidelines and commands to package, configure, and orchestrate the CodeGuru AI platform in production environments.

---

## 🏗 Containerized Stack Architecture

The production environment runs fully containerized via `docker-compose.prod.yml`:
1. **codeguru-nginx-prod**: Front-facing proxy routing frontend and backend REST services.
2. **codeguru-frontend-prod**: Next.js Node container serving static builds and Server Components.
3. **codeguru-backend-prod**: Multicore Uvicorn application serving FastAPI.
4. **codeguru-celery-prod**: Background queue task runner.
5. **codeguru-postgres-prod**: Persistent PostgreSQL database.
6. **codeguru-redis-prod**: High-speed cache and Celery broker.
7. **codeguru-prometheus-prod**: Metrics scraper targeting the backend instrumentations.
8. **codeguru-grafana-prod**: Dashboards dashboard tool visualizing system rates/latencies.

---

## 🚀 Step-by-Step Deploy Guide

### 1. Configure Production Environment Variables
Create `.env` file at the root:
```env
# Database Settings
POSTGRES_USER=guru_admin
POSTGRES_PASSWORD=supersecurepassword1234
POSTGRES_DB=codeguru_production

# Cache Settings
REDIS_HOST=redis
REDIS_PORT=6379

# Security Settings
SECRET_KEY=yoursecretkeyforjwtcreationmustbeextremelylong1234567890
GRAFANA_ADMIN_PASSWORD=grafana_admin_password

# LLM Providers
OPENAI_API_KEY=sk-proj-prodkeyhere
```

### 2. Run Production Setup
Build images and launch the cluster in detached mode:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Apply Migrations Inside Container
Execute database schema updates directly within the active backend container:
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 📈 System Monitoring & Metrics

Once running, metrics services can be accessed at:
- **FastAPI Endpoints**: `http://localhost/api/v1/health`
- **Prometheus Scrapers**: `http://localhost:9090`
- **Grafana Visualization**: `http://localhost:3000` (Default credentials: `admin` / `grafana_admin_password`)

### Grafana Dashboard Setup
1. Log into Grafana.
2. Navigate to **Connections > Data Sources** and add a Prometheus data source pointing to `http://prometheus:9090`.
3. Go to **Dashboards > Import** and load `/var/lib/grafana/dashboards/codeguru.json` to view preloaded FastAPI request tracking charts.
