# Docker Container Separation Plan

## Current State
- Single multi-stage Dockerfile (`deploy/Dockerfile`)
- Builds both frontend (TanStack Start) and backend (Django/DRF) in one container
- Uses nginx to serve both
- Single deployment unit

## Goal
Separate into independent, containerized services with proper orchestration

---

## Plan

### 1. Create Backend Dockerfile
**File:** `backend/Dockerfile`

- Use multi-stage build with `uv` for Python dependencies
- Copy only backend code
- Expose port 8000
- Run Django with gunicorn (production) or runserver (dev)
- Handle static files via Django's whitenoise or similar

### 2. Create Frontend Dockerfile
**File:** `frontend/Dockerfile`

- Multi-stage build: builder stage with pnpm
- Copy only frontend code
- Build TanStack Start app
- Runtime stage with Node.js
- Expose port 3000
- Run TanStack Start production server

### 3. Create Docker Compose Configuration
**File:** `docker-compose.yml`

Services:
- `backend`: Django/DRF API
  - Port 8000
  - Environment variables (DATABASE_URL, SECRET_KEY, etc.)
  - Volumes for media/uploads
- `frontend`: TanStack Start
  - Port 3000
  - Environment variables (VITE_API_URL, VITE_STRIPE_PUBLISHABLE)
  - Depends on backend
- `db`: PostgreSQL (if not using external DB)
- Optional: `nginx` reverse proxy in front of both

### 4. Update Nginx Configuration (Optional)
**File:** `deploy/nginx.conf`

If keeping nginx as reverse proxy:
- Route `/api/*` to backend:8000
- Route `/*` to frontend:3000
- Handle static/media from backend volume

### 5. Create Development Compose
**File:** `docker-compose.dev.yml`

- Mount source code as volumes for hot reload
- Override CMD for development servers
- Expose additional ports for debugging

### 6. Update Deployment Scripts
**Files:** `deploy/start-server.sh`, CI/CD configs

- Update to handle multi-container deployment
- Separate health checks for each service
- Update environment variable handling

### 7. Environment Variables
**Files:** `.env.example`, deployment configs

Split into:
- `backend/.env` - Django settings, DB, secrets
- `frontend/.env` - Vite/build-time variables, API URL

---

## Benefits
✓ Independent scaling (scale frontend separately from backend)
✓ Separate deployments and rollbacks
✓ Clearer development workflow
✓ Better resource allocation
✓ Easier debugging and logs
✓ True microservices architecture

## Migration Steps
1. Create new Dockerfiles
2. Create docker-compose.yml
3. Test locally with `docker-compose up`
4. Update deployment pipeline
5. Migrate staging environment
6. Migrate production
7. Remove old `deploy/Dockerfile`