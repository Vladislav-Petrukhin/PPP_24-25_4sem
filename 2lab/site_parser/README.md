1. pip install -r requirements.txt
2. Настройте .env
3. alembic upgrade head
4. Запустите Redis (docker run -p 6379:6379 redis)
5. uvicorn app.main:app --reload
6. celery -A celery_worker.celery worker --loglevel=info
