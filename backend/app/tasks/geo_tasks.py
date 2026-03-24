import asyncio

from app.db.session import AsyncSessionLocal
from app.services.ingestion_service import seed_geo_data
from app.tasks.celery_app import celery_app


@celery_app.task(name="geo.seed_data")
def seed_data_task(reset_first: bool = False):
    async def _run():
        async with AsyncSessionLocal() as session:
            stats = await seed_geo_data(session, reset_first=reset_first)
            return stats.__dict__

    return asyncio.run(_run())
