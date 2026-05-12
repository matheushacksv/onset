# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plataforma interna modular (Onset). Backend Django Ninja + frontend Nuxt 4. Módulos atuais: `accounts` (auth/JWT/equipe) e `onboarding` (formulário multi-step + geração IA de material de vendas + editor manual + assistente IA no editor). Deploy via Docker Swarm + Traefik.

## Commands

### Backend
```bash
cd backend
uv run python manage.py runserver           # dev server (porta 8000)
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py makemigrations <app>
uv run python manage.py qcluster            # worker django-q (tasks assíncronas)
uv run python manage.py build_knowledge     # popula PgVector com MDs do knowledge base (idempotente). Use --recreate para zerar.
```

### Frontend
```bash
cd frontend
npm run dev      # dev server (porta 3000)
npm run build
npm run preview
```

### Deploy (produção, Docker Swarm)
```bash
git pull
docker compose build backend worker frontend
docker service update --force onset_backend onset_worker onset_frontend
```
`build_knowledge` roda automaticamente em background no CMD do `backend/Dockerfile`.

## Architecture

### Backend (`backend/`)
- **Django Ninja** via `NinjaExtraAPI` com `JWTAuth()` global — todos os endpoints exigem Bearer token por padrão
- `core/api.py` é o roteador central; cada app registra seu router aqui via `api.add_router()`
- Autenticação: `django-ninja-jwt` — endpoints `/api/token/pair` e `/api/token/refresh` são públicos (`auth=None`)
- Custom User model em `accounts/` com email como `USERNAME_FIELD` (sem username)
- Storage: S3/MinIO via `django-storages` (boto3) — configurado por env vars
- **django-q** (ORM broker) para tarefas assíncronas — worker é o service `onset_worker`. Q_CLUSTER configurado em `core/settings.py`.
- **Cache**: `DatabaseCache` (tabela `django_cache` no Postgres). Compartilhado entre web e worker. `createcachetable` roda no CMD do Dockerfile.

**Adicionar novo módulo**: criar `backend/<nome>/` com `models.py`, `api.py` (router Ninja), `schemas.py`. Registrar em `INSTALLED_APPS` e `core/api.py`.

### Módulo `onboarding`
- **Formulário multi-step** persistido em `OnboardingForm`
- **Geração IA de material** (`GeneratedMaterial`): 3 agents paralelos (CRM, Closing, Qualification) via `agents/workflow.py` rodando com Agno + `gpt-5.4-nano`. Disparado por `POST /{id}/generate` → `tasks.generate_materials_task` (django-q)
- **Knowledge base** PgVector populado por `management/commands/build_knowledge.py` a partir de MDs. Runtime usa singleton `get_knowledge()` (só conecta, não recria)
- **Editor manual** do material — usuário edita JSON estruturado por aba (CRM funis/etapas/cadências, Closing objeções/scripts, Qualification fluxo WhatsApp/pitch)
- **Assistente IA no editor** (`agents/assistant.py`): `AssistantSession` por turno com tool-calling agent. 3 conjuntos de tools mutam `self.draft` (closure) e persistem ao final. Endpoint `POST /materials/assist`. Prewarm fire-and-forget via `POST /materials/assist/prepare` (django-q, debounce 10min em cache). `build_warm_agent()` no prewarm = sem tools/knowledge.
- Pipedrive integration em `pipedrive_services.py` (sync de funis/etapas)

### Frontend (`frontend/`)
- Nuxt 4 — estrutura em `app/` (não `src/`)
- `@nuxt/ui` v4 para componentes — CSS em `assets/css/main.css` com `@import "tailwindcss"` e `@import "@nuxt/ui"`
- Proxy `/api/**` → `http://localhost:8000/api/**` configurado em `nuxt.config.ts` (sem CORS em dev)
- Auth state via `useAuth()` composable — tokens em cookies (`access_token`, `refresh_token`)
- `middleware/auth.global.ts` protege todas as rotas; `/login` é a única pública
- Componentes namespaced `components/ob/*.vue` → `<ObXxx>` (auto-import Nuxt)
- Composables: `useAuth`, `useOnboarding` (CRUD + prepareAssistant fire-and-forget), `useAssistant` (chat IA editor)
- Editor de material em `pages/onboarding/[id]/materials.vue` — toggle entre `ObDataDrawer` (contexto onboarding) e `ObAssistantPanel` (chat IA)

### Design System
Referência visual em `backend/design-system.html`. Padrões:
- Background: `#0a0a0a` (neutral-950), modo dark
- Cards: `bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl` com `.border-gradient`
- Botão primário: `bg-white text-neutral-900 rounded-full`
- Fonte: Inter

## Environment

Backend requer `.env` em `backend/` com:
```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost
DATABASE_URL=postgres://...           # Postgres com extensão pgvector
OPENAI_API_KEY=                       # agents Agno
# S3/MinIO (opcional em dev)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=
# Pipedrive (opcional)
PIPEDRIVE_API_TOKEN=
```
