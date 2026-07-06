[![tests](https://github.com/philippeducasse/zirkusmond/actions/workflows/tests.yml/badge.svg)](https://github.com/philippeducasse/zirkusmond/actions/workflows/tests.yml)
[![staging](https://github.com/philippeducasse/zirkusmond/actions/workflows/staging.yml/badge.svg)](https://github.com/philippeducasse/zirkusmond/actions/workflows/staging.yml)
[![prod](https://github.com/philippeducasse/zirkusmond/actions/workflows/prod.yml/badge.svg)](https://github.com/philippeducasse/zirkusmond/actions/workflows/prod.yml)

# Zirkusmond

Website and booking platform for Zirkusmond: show listings, ticket reservations, QR-code ticket scanning, venue rentals, and a newsletter, backed by a Django app with a Vue/Vite frontend.

## Stack

- **Backend**: Django (`backend/`), managed with [uv](https://docs.astral.sh/uv/), Python 3.12. Key apps: `shows`, `reservations` (incl. payments and QR scanning), `rentals`, `newsletter`, `stats`.
- **Frontend**: Vue 3 + Vite (`frontend/`), Tailwind CSS.
- **Deploy**: Dockerized, deployed via GitHub Actions to `staging` and `prod` branches (see `deploy/` and `.github/workflows/`).

## Getting started

Backend:

```bash
cd backend
uv sync
uv run manage.py migrate
uv run manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev       # dev server
npm run tailwind  # watch & rebuild Tailwind CSS into backend/static/css
```

Required environment variables (Django secret key, DB, email, Stripe/PayPal keys, etc.) are loaded via `.envrc`/direnv — see that file for the full list. Never commit real secret values; use placeholders/local overrides instead.

## Testing

```bash
cd backend
uv run pytest
```

Tests run automatically on every push/PR via the `tests` GitHub Actions workflow.

## Contributing

- Branch off `main` for new work; `staging` and `prod` are deploy branches driven by their own workflows, don't commit directly to them.
- Install the pre-commit hooks before making changes: `pre-commit install`. They run `ruff` (lint + format) on the backend and basic whitespace/YAML/JSON/merge-conflict checks on every commit.
- Backend code is linted/formatted with `ruff` (`uv run ruff check --fix` / `uv run ruff format`); keep to the project's `line-length = 100` (see `backend/pyproject.toml`).
- Add or update tests for any backend logic change and make sure `uv run pytest` passes before opening a PR.
- Keep PRs focused and small where possible; describe _why_ a change is needed, not just what changed.
- Open a PR against `main`; CI (tests workflow) must pass before merging.

# qr code duplication

# cookie popover

# add way for juan to change videos && images

# early bird tickets

# tickets umbuchen
