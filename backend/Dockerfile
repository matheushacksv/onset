FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
COPY . .
CMD ["sh", "-c", "\
    uv run python manage.py migrate --noinput && \
    uv run python manage.py createcachetable && \
    uv run python manage.py collectstatic --noinput && \
    (uv run python manage.py build_knowledge >/proc/1/fd/1 2>/proc/1/fd/2 &) && \
    uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000 \
"]
