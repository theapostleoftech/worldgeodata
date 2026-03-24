from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.city import CityOut
from app.schemas.division import DivisionOut
from app.services.geo_service import get_cities_by_lga, get_lgas_by_state

router = APIRouter()


@router.get("/states/{state_id}/lgas", response_model=list[DivisionOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def state_lgas(state_id: int, db: AsyncSession = Depends(get_db_session)):
    return await get_lgas_by_state(db, state_id)


@router.get("/lgas/{lga_id}/cities", response_model=list[CityOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def lga_cities(lga_id: int, db: AsyncSession = Depends(get_db_session)):
    return await get_cities_by_lga(db, lga_id)
