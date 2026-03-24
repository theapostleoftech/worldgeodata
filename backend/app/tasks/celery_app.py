from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worldgeodata",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
