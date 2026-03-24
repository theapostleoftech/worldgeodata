from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis, rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.city import CityOut
from app.schemas.division import DivisionOut
from app.services.cache_service import get_or_set_cache
from app.services.geo_service import (
    get_division,
    get_division_children,
    get_division_cities,
    list_country_divisions,
)

router = APIRouter()


@router.get(
    "/countries/{country_id}/divisions",
    response_model=list[DivisionOut],
    dependencies=[Depends(rate_limit), Depends(verify_api_key)],
)
async def country_divisions(
    country_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    async def fetch():
        _, rows = await list_country_divisions(db, country_id=country_id, page=page, page_size=page_size)
        return [DivisionOut.model_validate(row).model_dump() for row in rows]

    data = await get_or_set_cache(redis, f"divisions:{country_id}:{page}:{page_size}", fetch)
    return [DivisionOut.model_validate(row) for row in data]


@router.get("/divisions/{division_id}", response_model=DivisionOut, dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def division(division_id: int, db: AsyncSession = Depends(get_db_session)):
    row = await get_division(db, division_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Division not found")
    return row


@router.get(
    "/divisions/{division_id}/children",
    response_model=list[DivisionOut],
    dependencies=[Depends(rate_limit), Depends(verify_api_key)],
)
async def division_children(division_id: int, db: AsyncSession = Depends(get_db_session)):
    rows = await get_division_children(db, division_id)
    return rows


@router.get(
    "/divisions/{division_id}/cities",
    response_model=list[CityOut],
    dependencies=[Depends(rate_limit), Depends(verify_api_key)],
)
async def division_cities(division_id: int, db: AsyncSession = Depends(get_db_session)):
    rows = await get_division_cities(db, division_id)
    return rows
