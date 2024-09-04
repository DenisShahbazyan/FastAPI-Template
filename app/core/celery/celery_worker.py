from celery import Celery
from celery.schedules import crontab

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

celery.conf.update(
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_cls='celery_aio_pool:AsyncIOPool',  # Только для асинхронных задач
    worker_pool='celery_aio_pool.AsyncIOPool',  # Только для асинхронных задач
)

celery.autodiscover_tasks(['app.api.tasks.async_tasks', 'app.api.tasks.sync_tasks'])

celery.conf.beat_schedule = {
    'reset-tokens-daily': {
        'task': 'app.api.tasks.user.function_name',  # function_name
        'schedule': crontab(hour=21, minute=0),  # 00:00 по МСК
    },
}
