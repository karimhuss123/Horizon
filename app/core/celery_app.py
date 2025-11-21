from celery import Celery
from app.core.config import settings

def create_celery_app() -> Celery:
    celery_app = Celery(
        "horizon",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL
    )
    celery_app.autodiscover_tasks(settings.CELERY_TASK_FILES)
    return celery_app

celery_app = create_celery_app()
