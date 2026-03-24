from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.geo import NearbyResultOut, ReverseGeocodeOut
from app.services.geo_service import nearby_entities, reverse_geocode

router = APIRouter()


@router.get("/nearby", response_model=list[NearbyResultOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def nearby(
    lat: float = Query(),
    lng: float = Query(),
    radius_km: float = Query(default=25, gt=0, le=200),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    return await nearby_entities(db, lat=lat, lng=lng, radius_km=radius_km, limit=limit)


@router.get(
    "/reverse-geocode",
    response_model=ReverseGeocodeOut,
    dependencies=[Depends(rate_limit), Depends(verify_api_key)],
)
async def reverse_geo(lat: float = Query(), lng: float = Query(), db: AsyncSession = Depends(get_db_session)):
    return await reverse_geocode(db, lat=lat, lng=lng)
