from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis, rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.city import CityOut
from app.services.cache_service import get_or_set_cache
from app.services.geo_service import get_city, list_cities

router = APIRouter(prefix="/cities")


@router.get("", response_model=list[CityOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def cities(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    async def fetch():
        _, rows = await list_cities(db, page=page, page_size=page_size)
        return [CityOut.model_validate(row).model_dump() for row in rows]

    data = await get_or_set_cache(redis, f"cities:{page}:{page_size}", fetch)
    return [CityOut.model_validate(row) for row in data]


@router.get("/{city_id}", response_model=CityOut, dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def city(city_id: int, db: AsyncSession = Depends(get_db_session)):
    row = await get_city(db, city_id)
    if row is None:
        raise HTTPException(status_code=404, detail="City not found")
    return row
