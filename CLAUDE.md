# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plataforma interna modular. Backend Django Ninja + frontend Nuxt 4. Atualmente contém apenas autenticação (login/JWT). Novos módulos viram Django apps no backend e páginas no frontend.

## Commands

### Backend
```bash
cd backend
uv run python manage.py runserver       # dev server (porta 8000)
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py makemigrations <app>
```

### Frontend
```bash
cd frontend
npm run dev      # dev server (porta 3000)
npm run build
npm run preview
```

## Architecture

### Backend (`backend/`)
- **Django Ninja** via `NinjaExtraAPI` com `JWTAuth()` global — todos os endpoints exigem Bearer token por padrão
- `core/api.py` é o roteador central; cada app registra seu router aqui via `api.add_router()`
- Autenticação: `django-ninja-jwt` — endpoints `/api/token/pair` e `/api/token/refresh` são públicos (`auth=None`)
- Custom User model em `accounts/` com email como `USERNAME_FIELD` (sem username)
- Storage: S3/MinIO via `django-storages` (boto3) — configurado por env vars
- Celery com Redis como broker para tarefas assíncronas

**Adicionar novo módulo**: criar `backend/apps/<nome>/` com `models.py`, `api.py` (router Ninja), `schemas.py`. Registrar em `INSTALLED_APPS` e `core/api.py`.

### Frontend (`frontend/`)
- Nuxt 4 — estrutura em `app/` (não `src/`)
- `@nuxt/ui` v4 para componentes — CSS em `assets/css/main.css` com `@import "tailwindcss"` e `@import "@nuxt/ui"`
- Proxy `/api/**` → `http://localhost:8000/api/**` configurado em `nuxt.config.ts` (sem CORS em dev)
- Auth state via `useAuth()` composable — tokens em cookies (`access_token`, `refresh_token`)
- `middleware/auth.global.ts` protege todas as rotas; `/login` é a única pública

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
# S3/MinIO (opcional em dev)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=
# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```
