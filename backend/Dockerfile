FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
    libffi8 fonts-inter \
    && rm -rf /var/lib/apt/lists/*
COPY . .
CMD ["sh", "-c", "\
    uv run python manage.py migrate --noinput && \
    uv run python manage.py createcachetable && \
    uv run python manage.py collectstatic --noinput && \
    (uv run python manage.py build_knowledge >/proc/1/fd/1 2>/proc/1/fd/2 &) && \
    uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000 \
"]
