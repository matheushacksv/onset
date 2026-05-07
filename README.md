# Farol

Plataforma interna de onboarding de clientes de assessoria com geração de materiais via IA.

## Stack

- **Backend:** Django 6 + Django Ninja + PostgreSQL (pgvector) + MinIO
- **Frontend:** Nuxt 4 + @nuxt/ui
- **IA:** OpenAI via Agno — geração de scripts CRM, fechamento e qualificação
- **Filas:** Django-Q2
- **Deploy:** Docker Compose + Nginx

## Módulos

| Módulo | Descrição |
|--------|-----------|
| `accounts` | Autenticação JWT, usuários e permissões por grupo |
| `onboarding` | Cadastro de clientes, geração de materiais com IA, knowledge base vetorial |

## Desenvolvimento

### Pré-requisitos

- Python 3.13+ com `uv`
- Node 22+
- Docker (para postgres e redis)

### Backend

```bash
cd backend
docker compose up -d          # sobe postgres + redis
cp .env.example .env          # preencher variáveis
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse em `http://localhost:3000`.

### Indexar knowledge base

```bash
cd backend
uv run python manage.py index_knowledge           # incremental
uv run python manage.py index_knowledge --recreate # reindexar tudo
```

## Variáveis de ambiente (`backend/.env`)

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

MINIO_ENDPOINT_URL=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_BUCKET_NAME=

OPENAI_API_KEY=
```

## Deploy

```bash
# No servidor (primeira vez)
git clone <repo> /app && cd /app
nano backend/.env
certbot certonly --standalone -d app.dominio.com -d api.dominio.com
docker compose up -d --build
docker compose exec backend uv run python manage.py migrate
docker compose exec backend uv run python manage.py createsuperuser
docker compose exec backend uv run python manage.py index_knowledge

# Atualizações
git pull && docker compose up -d --build
```

## Permissões

| Grupo | Acesso |
|-------|--------|
| Assessor | Criar e visualizar onboardings, gerar materiais |
| Desenvolvedor | Somente leitura — sem criar onboardings |
| Superuser | Acesso total + painel admin |
