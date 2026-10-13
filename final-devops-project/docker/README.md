# Docker Setup & Containerization

This directory contains containerization files for building and testing the TaskBoard microservices locally using Docker and Docker Compose.

---

## 1. Services

- **Database**: PostgreSQL 16 Alpine (`postgres-data` named volume for persistence)
- **Backend**: FastAPI Python 3.12 (`Dockerfile.backend`)
- **Frontend**: React + Vite served via Nginx Alpine (`Dockerfile.frontend`)

---

## 2. Docker Build & Run Commands

### Run Everything with Docker Compose
```bash
cd final-devops-project/docker
docker compose up -d --build

# Verify running containers
docker compose ps

# Check logs
docker compose logs -f backend
```

Access points:
- Frontend: `http://localhost:3000`
- Backend Swagger API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Build Images Individually
```bash
# Build Backend
docker build -t ghcr.io/apurvdugar/taskboard-backend:latest -f Dockerfile.backend ../application/backend

# Build Frontend
docker build -t ghcr.io/apurvdugar/taskboard-frontend:latest -f Dockerfile.frontend ../application/frontend
```
