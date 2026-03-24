from typing import Any

from sqlalchemy import Select, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_division import AdminDivision
from app.models.city import City
from app.models.country import Country


def _page(query: Select[Any], page: int, page_size: int) -> Select[Any]:
    return query.offset((page - 1) * page_size).limit(page_size)


async def list_countries(db: AsyncSession, page: int, page_size: int):
    total = await db.scalar(select(func.count(Country.id)))
    rows = await db.scalars(_page(select(Country).order_by(Country.name), page, page_size))
    return total or 0, list(rows)


async def get_country_by_id(db: AsyncSession, country_id: int):
    return await db.scalar(select(Country).where(Country.id == country_id))


async def get_country_by_iso2(db: AsyncSession, iso2: str):
    return await db.scalar(select(Country).where(func.lower(Country.iso2) == iso2.lower()))


async def list_country_divisions(db: AsyncSession, country_id: int, page: int, page_size: int):
    total = await db.scalar(select(func.count(AdminDivision.id)).where(AdminDivision.country_id == country_id))
    rows = await db.scalars(
        _page(
            select(AdminDivision)
            .where(AdminDivision.country_id == country_id)
            .order_by(AdminDivision.level, AdminDivision.name),
            page,
            page_size,
        )
    )
    return total or 0, list(rows)


async def get_division(db: AsyncSession, division_id: int):
    return await db.scalar(select(AdminDivision).where(AdminDivision.id == division_id))


async def get_division_children(db: AsyncSession, division_id: int):
    rows = await db.scalars(
        select(AdminDivision).where(AdminDivision.parent_id == division_id).order_by(AdminDivision.name)
    )
    return list(rows)


async def get_division_cities(db: AsyncSession, division_id: int):
    rows = await db.scalars(select(City).where(City.admin_division_id == division_id).order_by(City.name))
    return list(rows)


async def list_cities(db: AsyncSession, page: int, page_size: int):
    total = await db.scalar(select(func.count(City.id)))
    rows = await db.scalars(_page(select(City).order_by(City.name), page, page_size))
    return total or 0, list(rows)


async def get_city(db: AsyncSession, city_id: int):
    return await db.scalar(select(City).where(City.id == city_id))


async def get_lgas_by_state(db: AsyncSession, state_id: int):
    rows = await db.scalars(
        select(AdminDivision)
        .where(AdminDivision.parent_id == state_id, AdminDivision.type.in_(["lga", "local_government_area"]))
        .order_by(AdminDivision.name)
    )
    return list(rows)


async def get_cities_by_lga(db: AsyncSession, lga_id: int):
    return await get_division_cities(db, lga_id)


async def weighted_search(db: AsyncSession, query: str, page: int, page_size: int):
    q = f"%{query.strip().lower()}%"

    city_q = select(
        literal("city").label("entity_type"),
        City.id.label("id"),
        City.name.label("name"),
        literal(100).label("score"),
        City.country_id.label("country_id"),
        City.admin_division_id.label("parent_id"),
    ).where(func.lower(City.name).like(q))

    division_q = select(
        literal("division").label("entity_type"),
        AdminDivision.id.label("id"),
        AdminDivision.name.label("name"),
        case(
            (AdminDivision.type.in_(["lga", "county", "local_government_area"]), 80),
            (AdminDivision.level == 1, 60),
            else_=50,
        ).label("score"),
        AdminDivision.country_id.label("country_id"),
        AdminDivision.parent_id.label("parent_id"),
    ).where(func.lower(AdminDivision.name).like(q))

    country_q = select(
        literal("country").label("entity_type"),
        Country.id.label("id"),
        Country.name.label("name"),
        literal(40).label("score"),
        Country.id.label("country_id"),
        literal(None).label("parent_id"),
    ).where(or_(func.lower(Country.name).like(q), func.lower(Country.iso2).like(q), func.lower(Country.iso3).like(q)))

    unioned = city_q.union_all(division_q, country_q).subquery()
    total = await db.scalar(select(func.count()).select_from(unioned))
    rows = await db.execute(
        select(unioned)
        .order_by(unioned.c.score.desc(), unioned.c.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return total or 0, [dict(row._mapping) for row in rows]


async def nearby_entities(db: AsyncSession, lat: float, lng: float, radius_km: float, limit: int):
    distance_expr = 6371 * func.acos(
        func.cos(func.radians(lat))
        * func.cos(func.radians(City.latitude))
        * func.cos(func.radians(City.longitude) - func.radians(lng))
        + func.sin(func.radians(lat)) * func.sin(func.radians(City.latitude))
    )
    rows = await db.execute(
        select(
            literal("city").label("entity_type"),
            City.id,
            City.name,
            City.latitude,
            City.longitude,
            distance_expr.label("distance_km"),
        )
        .where(City.latitude.is_not(None), City.longitude.is_not(None))
        .having(distance_expr <= radius_km)
        .order_by(distance_expr.asc())
        .limit(limit)
    )
    return [dict(row._mapping) for row in rows]


async def reverse_geocode(db: AsyncSession, lat: float, lng: float):
    nearest = await nearby_entities(db, lat, lng, radius_km=50, limit=1)
    if not nearest:
        return {"country": None, "division_path": [], "city": None}

    city = await get_city(db, int(nearest[0]["id"]))
    if city is None:
        return {"country": None, "division_path": [], "city": None}

    country = await get_country_by_id(db, city.country_id)

    path = []
    current = await get_division(db, city.admin_division_id) if city.admin_division_id else None
    while current is not None:
        path.append(current.name)
        current = await get_division(db, current.parent_id) if current.parent_id else None
    path.reverse()

    return {"country": country.name if country else None, "division_path": path, "city": city.name}
