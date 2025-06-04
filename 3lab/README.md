# Site Parser & Graph Builder

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) HTTP API + WS
uvicorn app.main:app --reload

# 2) Celery worker (в отдельном окне/терминале)
celery -A app.core.celery_app worker -l info

# 3) Alembic (при первом запуске)
alembic upgrade head
```

## Эндпоинты

* `POST /api/sign-up/`
* `POST /api/login/` → Bearer JWT
* `GET /api/users/me/`
* `POST /api/parse_website`
* `GET /api/parse_status?task_id=…`
* `WS /ws?token=<JWT>`

Форматы сообщений по WS — см. лабораторное ТЗ.
