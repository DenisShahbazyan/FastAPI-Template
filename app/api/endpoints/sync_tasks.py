from celery.result import AsyncResult
from fastapi import APIRouter

from app.api.tasks.async_tasks import task_name
from app.core.celery.celery_worker import celery

router = APIRouter(prefix='/example', tags=['example'])


@router.post('function_name')
async def function_name(string: str):
    task = task_name.delay(string)
    return task


@router.get('/result/{task_id}')
async def get_recognition_result(task_id: str):
    task = AsyncResult(task_id, app=celery)
    if task.state == 'PENDING':
        return {'status': 'processing'}
    elif task.state == 'SUCCESS':
        return {'status': 'completed'}
    else:
        return {'status': 'failed'}
