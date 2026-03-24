from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis, rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.country import CountryOut
from app.services.cache_service import get_or_set_cache
from app.services.geo_service import get_country_by_id, get_country_by_iso2, list_countries

router = APIRouter(prefix="/countries")


@router.get("", response_model=list[CountryOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def countries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    async def fetch():
        _, rows = await list_countries(db, page=page, page_size=page_size)
        return [CountryOut.model_validate(row).model_dump() for row in rows]

    data = await get_or_set_cache(redis, f"countries:{page}:{page_size}", fetch)
    return [CountryOut.model_validate(row) for row in data]


@router.get("/{country_id:int}", response_model=CountryOut, dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def country_by_id(country_id: int, db: AsyncSession = Depends(get_db_session)):
    country = await get_country_by_id(db, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.get("/iso/{iso2}", response_model=CountryOut, dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def country_by_iso2(iso2: str, db: AsyncSession = Depends(get_db_session)):
    country = await get_country_by_iso2(db, iso2)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country
