# AGENTS.md

## Quick Reference

```bash
# Backend (from backend/)
uv run python manage.py runserver          # dev server :8000
uv run python manage.py migrate
uv run python manage.py makemigrations <app>
uv run pytest                              # run tests
uv run pytest onboarding/tests/            # single app tests

# Frontend (from frontend/)
npm run dev                                # dev server :3000
npm run build

# Infrastructure
docker compose up -d                       # postgres (pgvector) + redis
```

## Architecture Corrections (vs CLAUDE.md)

CLAUDE.md has stale or inaccurate claims. Trust these facts:

- **Task queue is Django-Q2 with ORM broker**, not Celery+Redis. Redis is in docker-compose but unused by the queue (`Q_CLUSTER.orm = 'default'`).
- **Apps live directly under `backend/`** (`accounts/`, `onboarding/`), NOT in `backend/apps/<name>/`. There is no `apps/` directory.
- **Python 3.13+** and **Django 6.0** (not older versions).

## Backend

### Module Pattern

Each module has: `models.py`, `api.py` (Ninja router), `schemas.py`, `tasks.py`.  
Register new routers in `core/api.py` via `api.add_router('prefix/', router)`.

### Auth

- All endpoints require JWT by default (global `JWTAuth()` on `NinjaExtraAPI`).
- Public endpoints must explicitly set `auth=None`.
- JWT tokens: access 30min, refresh 7 days.
- Custom User model in `accounts/` — email is `USERNAME_FIELD`, no username field.

### AI Agents (onboarding module)

- Framework: `agno` v2.6.4 with OpenAI models (GPT-5.4-nano).
- RAG: pgvector extension on PostgreSQL 17, knowledge base from markdown files in `onboarding/knowledge/`.
- `MaterialWorkflow` runs 4 agents (1 validator + 3 generators in parallel via `asyncio.gather`).
- Generation is async via Django-Q2 tasks.

### agno v2.6.4 API (critical quirks)

- **Pydantic output schema** param is `output_schema=` (NOT `response_model` or `output_model` — `output_model` is for model/LLM provider instances).
- `output_schema` must be a `BaseModel` subclass. `list[str]` (a `GenericAlias`) fails — wrap it in a schema like `class QualityAlerts(BaseModel): alerts: list[str]`.
- Parsed result lives in `val_resp.content` (when `output_schema` is a `BaseModel`, `.content` is the parsed instance).
- `Knowledge.insert(path=)` accepts a **single string** — loop files for multiple; `insert_many(paths=)` also works.
- Knowledge base uses OpenAI embeddings — `OPENAI_API_KEY` must be in `os.environ` (agno's OpenAI client reads env, not python-decouple). Set via `os.environ.setdefault('OPENAI_API_KEY', config('OPENAI_API_KEY'))` in `settings.py`.
- `PgVector` constructor expects `db_url`. The agno library looks for `DATABASE_URL` env var. Either set it in `.env` or construct from `POSTGRES_*` vars.

### Database

- PostgreSQL 17 with `pgvector` extension (docker-compose provides `pgvector/pgvector:pg17`).
- Env vars: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.
- `init.sql` creates the vector extension automatically.

### Settings

- Env loading: `python-decouple` (reads `.env` in `backend/`). Does NOT inject into `os.environ` — SDKs (OpenAI, httpx) that read env vars directly must be set explicitly (see `core/settings.py`).
- Locale: `pt-BR`, timezone `America/Sao_Paulo`.
- Storage: S3/MinIO via `django-storages` (env: `MINIO_*` vars).
- Django-Q2 timeout default is 60s — may be too short for AI generation tasks.

## Frontend

### Structure

- Nuxt 4 with source in `app/` (not `src/`).
- Components: `@nuxt/ui` v4 + Pinia for state.
- CSS: Tailwind via `@nuxt/ui` import in `assets/css/main.css`.

### API Proxy

`/api/**` proxied to `http://localhost:8000/api/**` in `nuxt.config.ts` — no CORS issues in dev.

### Auth Flow

- `useAuth()` composable stores tokens in cookies (`access_token` 1h, `refresh_token` 7d).
- `fetchAuth<T>()` wrapper auto-refreshes on 401.
- `middleware/auth.global.ts` — public routes: `/login`, `/forgot-password`, `/reset-password`.

## Testing

- `pytest-django` with `DJANGO_SETTINGS_MODULE = core.settings`.
- Run from `backend/`: `uv run pytest`.
- No frontend tests configured.
- No CI pipeline exists yet.

## Conventions

- No linter, formatter, or pre-commit hooks configured.
- Design system reference: `backend/design-system.html` (dark mode, Inter font, neutral-950 bg).
- `.gitignore` excludes `onboarding/knowledge/` and `pytest.ini` — don't commit those.
