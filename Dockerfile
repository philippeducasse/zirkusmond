# ── Stage 1: Frontend build ───────────────────────────────────────────────────
FROM node:22-slim AS frontend-builder
WORKDIR /build/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./

# tailwind → /build/backend/static/css/tailwind.css
# vite     → /build/backend/static/media/dist/
RUN mkdir -p /build/backend/static/css /build/backend/static/media/dist && \
    npm run tailwind && \
    npm run build && \
    cp -r node_modules/@glidejs /build/backend/static/media/dist/

# ── Stage 2: Python venv ──────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS python-builder

ENV UV_PROJECT_ENVIRONMENT=/usr/src/backend/.venv

COPY backend/pyproject.toml backend/uv.lock /build/
RUN uv sync --frozen --no-dev --project /build

# ── Stage 3: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

WORKDIR /usr/src

COPY start-server.sh .
RUN chmod +x start-server.sh

COPY --from=python-builder /usr/src/backend/.venv ./backend/.venv
COPY backend ./backend
COPY --from=frontend-builder /build/backend/static ./backend/static

COPY ./nginx.default /etc/nginx/sites-available/default
RUN mkdir -p /srv/data/static /srv/data/media

ENV PATH="/usr/src/backend/.venv/bin:$PATH"

EXPOSE 8000

CMD ["/usr/src/start-server.sh"]