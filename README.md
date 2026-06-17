# marketplace-campaign-rules

FastAPI-сервис для управления `target_status` рекламных кампаний по иерархии правил из тестового задания. Требования из PDF реализованы как отдельные rule-компоненты с единым интерфейсом, журналированием вычислений и PostgreSQL-схемой.

## Что внутри

- FastAPI + SQLAlchemy 2.0
- PostgreSQL + Alembic
- Docker Compose
- Rule engine с расширяемой цепочкой правил
- CRUD кампаний и расписаний
- История вычислений
- Unit-тесты для правил и integration-тест API
- Однострочный дамп PostgreSQL

## Структура

```text
.
├── alembic
├── app
│   ├── api
│   ├── core
│   ├── db
│   ├── models
│   ├── repositories
│   ├── rules
│   └── services
├── docker
│   └── postgres-init
├── tests
│   ├── integration
│   └── unit
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Правила

Проверяются строго по порядку:

1. `management_disabled`
2. `schedule`
3. `low_stock`
4. `budget_exceeded`
5. fallback: `active`

Добавление нового правила не требует изменений в движке — достаточно реализовать класс с интерфейсом `Rule` и добавить его в конфигурацию движка.

## Запуск через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Приложение будет доступно по адресу:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Тесты

```bash
docker compose exec api pytest -vv
```

## Миграции

```bash
alembic upgrade head
alembic downgrade -1
```

## SQL-дамп PostgreSQL

Готовый дамп схемы находится в файле:

```text
docker/postgres-init/001_schema.sql
```

Он автоматически применяется контейнером PostgreSQL при первом запуске.

## Ключевые решения

- `RuleEngine` ничего не знает о деталях конкретных правил.
- Расписание проверяется через отдельный сервис `ScheduleMatcher`.
- `POST /campaigns/{id}/evaluate` поддерживает `dry_run=true`.
- `GET /campaigns?needs_sync=true` возвращает кампании, где `current_status != target_status`.
- Логи вычислений содержат snapshot контекста в JSON.

## Основные эндпоинты

- `POST /campaigns`
- `GET /campaigns`
- `GET /campaigns/{id}`
- `PATCH /campaigns/{id}`
- `PUT /campaigns/{id}/schedule`
- `GET /campaigns/{id}/schedule`
- `DELETE /campaigns/{id}/schedule`
- `POST /campaigns/{id}/evaluate`
- `POST /campaigns/evaluate-all`
- `GET /campaigns/{id}/evaluation-history`
