from celery.exceptions import MaxRetriesExceededError

from app.core.celery.celery_worker import celery


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
async def task_name(self):
    try:
        pass  # Тут асинхронная функция
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            print(
                f'Задание не выполнено после {self.request.retries} попыток.'
                f'Исключение: {exc}'
            )
