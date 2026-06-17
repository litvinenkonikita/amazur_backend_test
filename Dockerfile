FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker/postgres-init ./docker/postgres-init
COPY tests ./tests

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .[dev]

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}"]