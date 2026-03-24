from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import rate_limit, verify_api_key
from app.db.session import get_db_session
from app.schemas.search import SearchResultOut
from app.services.geo_service import weighted_search

router = APIRouter(prefix="/search")


@router.get("", response_model=list[SearchResultOut], dependencies=[Depends(rate_limit), Depends(verify_api_key)])
async def search(
    q: str = Query(min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
):
    _, rows = await weighted_search(db, query=q, page=page, page_size=page_size)
    return rows
