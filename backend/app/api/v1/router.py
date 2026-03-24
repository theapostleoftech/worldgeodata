from fastapi import APIRouter

from app.api.v1.routes import cities, countries, divisions, geo, nigeria, search

api_router = APIRouter(prefix="/geo")
api_router.include_router(countries.router, tags=["countries"])
api_router.include_router(divisions.router, tags=["divisions"])
api_router.include_router(cities.router, tags=["cities"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(geo.router, tags=["geo"])
api_router.include_router(nigeria.router, tags=["nigeria"])
