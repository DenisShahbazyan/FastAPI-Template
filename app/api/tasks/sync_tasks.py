from app.core.celery.celery_worker import celery


@celery.task
def sync_task(argument):
    pass  # Тут синхронная функция, которая была вызвана из app/api/endpoints/sync_tasks.py  # noqa: E501
