#!/bin/sh

# Запуск redis-server в фоне
redis-server --daemonize yes

# Запуск celery worker
celery -A app.core.celery.celery_worker worker --loglevel=info &

# Запуск uvicorn
gunicorn app.main:app -c gunicorn_conf.py &

# Запуск celery flower
celery -A app.core.celery.celery_worker flower --port=5555 &

# Ожидание завершения всех процессов
wait
