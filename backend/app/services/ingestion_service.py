import asyncio
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.admin_division import AdminDivision
from app.models.city import City
from app.models.country import Country
from app.models.ingestion_log import IngestionLog


def _norm_name(value: str | None) -> str:
    return (value or "").strip().lower()


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class IngestionStats:
    countries: int = 0
    divisions: int = 0
    cities: int = 0
    duplicates: int = 0
    inconsistencies: int = 0


class GeoIngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stats = IngestionStats()
        self.country_index: dict[str, Country] = {}
        self.division_index: dict[tuple[int, int, str, int | None], AdminDivision] = {}
        self.city_index: dict[tuple[int, str, int | None], City] = {}

    async def run(self) -> IngestionStats:
        await self._create_log("combined", "started", {"message": "Ingestion started"})
        try:
            dr5hn = await self._fetch_json(f"{settings.DR5HN_BASE_URL}/json/countries+states+cities.json")
            nigeria = await self._fetch_json(settings.NIGERIA_LGA_DATASET_URL)

            await self._seed_countries_dr5hn(dr5hn)
            await self._seed_divisions_and_cities_dr5hn(dr5hn)
            await self._seed_nigeria_lga_data(nigeria)

            await self.db.commit()
            await self._create_log("combined", "completed", self.stats.__dict__)
            return self.stats
        except Exception as exc:
            await self.db.rollback()
            await self._create_log("combined", "failed", {"error": str(exc)})
            raise

    async def reset_geo_tables(self) -> None:
        await self.db.execute(delete(City))
        await self.db.execute(delete(AdminDivision))
        await self.db.execute(delete(Country))
        await self.db.commit()

    async def _fetch_json(self, url: str):
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def _create_log(self, source: str, status: str, details: dict[str, Any]) -> None:
        self.db.add(IngestionLog(source=source, status=status, details=details))
        await self.db.flush()

    async def _seed_countries_dr5hn(self, payload: list[dict[str, Any]]) -> None:
        for item in payload:
            iso2 = (item.get("iso2") or "").upper()
            iso3 = (item.get("iso3") or "").upper()
            name = item.get("name")
            if not iso2 or not name:
                self.stats.inconsistencies += 1
                continue

            existing = await self.db.scalar(select(Country).where(Country.iso2 == iso2))
            if existing:
                self.country_index[iso2] = existing
                continue

            country = Country(
                name=name,
                iso2=iso2,
                iso3=iso3 or iso2,
                phone_code=str(item.get("phone_code") or "") or None,
                capital=item.get("capital"),
                currency=item.get("currency") or item.get("currency_name"),
                latitude=_to_float(item.get("latitude")),
                longitude=_to_float(item.get("longitude")),
            )
            self.db.add(country)
            await self.db.flush()
            self.country_index[iso2] = country
            self.stats.countries += 1

    async def _seed_divisions_and_cities_dr5hn(self, payload: list[dict[str, Any]]) -> None:
        for item in payload:
            iso2 = (item.get("iso2") or "").upper()
            country = self.country_index.get(iso2)
            if country is None:
                continue

            for state in item.get("states") or []:
                state_name = state.get("name")
                if not state_name:
                    self.stats.inconsistencies += 1
                    continue
                state_div = await self._get_or_create_division(
                    country_id=country.id,
                    level=1,
                    div_type="state",
                    name=state_name,
                    parent_id=None,
                    latitude=_to_float(state.get("latitude")),
                    longitude=_to_float(state.get("longitude")),
                )

                for city in state.get("cities") or []:
                    city_name = city.get("name")
                    if not city_name:
                        self.stats.inconsistencies += 1
                        continue
                    await self._get_or_create_city(
                        country_id=country.id,
                        name=city_name,
                        admin_division_id=state_div.id,
                        latitude=_to_float(city.get("latitude")),
                        longitude=_to_float(city.get("longitude")),
                    )

    async def _seed_nigeria_lga_data(self, payload: list[dict[str, Any]]) -> None:
        nigeria = self.country_index.get("NG")
        if nigeria is None:
            self.stats.inconsistencies += 1
            return

        for state_item in payload:
            state_name = state_item.get("state")
            if not state_name:
                self.stats.inconsistencies += 1
                continue

            state_div = await self._get_or_create_division(
                country_id=nigeria.id,
                level=1,
                div_type="state",
                name=state_name,
                parent_id=None,
                latitude=None,
                longitude=None,
            )

            for lga in state_item.get("lgas") or []:
                lga_name = lga.get("name")
                if not lga_name:
                    self.stats.inconsistencies += 1
                    continue
                lga_div = await self._get_or_create_division(
                    country_id=nigeria.id,
                    level=2,
                    div_type="lga",
                    name=lga_name,
                    parent_id=state_div.id,
                    latitude=None,
                    longitude=None,
                )

                for town in lga.get("towns") or []:
                    if isinstance(town, str):
                        town_name = town
                    else:
                        town_name = town.get("name") if isinstance(town, dict) else None
                    if not town_name:
                        self.stats.inconsistencies += 1
                        continue
                    await self._get_or_create_city(
                        country_id=nigeria.id,
                        name=town_name,
                        admin_division_id=lga_div.id,
                        latitude=None,
                        longitude=None,
                    )

    async def _get_or_create_division(
        self,
        country_id: int,
        level: int,
        div_type: str,
        name: str,
        parent_id: int | None,
        latitude: float | None,
        longitude: float | None,
    ) -> AdminDivision:
        key = (country_id, level, _norm_name(name), parent_id)
        if key in self.division_index:
            self.stats.duplicates += 1
            return self.division_index[key]

        row = await self.db.scalar(
            select(AdminDivision).where(
                AdminDivision.country_id == country_id,
                AdminDivision.level == level,
                AdminDivision.parent_id.is_(parent_id),
                AdminDivision.name == name,
            )
        )
        if row:
            self.division_index[key] = row
            self.stats.duplicates += 1
            return row

        row = AdminDivision(
            name=name.strip(),
            level=level,
            type=div_type,
            parent_id=parent_id,
            country_id=country_id,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(row)
        await self.db.flush()
        self.division_index[key] = row
        self.stats.divisions += 1
        return row

    async def _get_or_create_city(
        self,
        country_id: int,
        name: str,
        admin_division_id: int | None,
        latitude: float | None,
        longitude: float | None,
    ) -> City:
        key = (country_id, _norm_name(name), admin_division_id)
        if key in self.city_index:
            self.stats.duplicates += 1
            return self.city_index[key]

        row = await self.db.scalar(
            select(City).where(
                City.country_id == country_id,
                City.admin_division_id.is_(admin_division_id),
                City.name == name,
            )
        )
        if row:
            self.city_index[key] = row
            self.stats.duplicates += 1
            return row

        row = City(
            name=name.strip(),
            country_id=country_id,
            admin_division_id=admin_division_id,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(row)
        await self.db.flush()
        self.city_index[key] = row
        self.stats.cities += 1
        return row


async def seed_geo_data(db: AsyncSession, reset_first: bool = False) -> IngestionStats:
    service = GeoIngestionService(db)
    if reset_first:
        await service.reset_geo_tables()
    return await service.run()


def run_seed_from_sync(db_factory, reset_first: bool = False) -> IngestionStats:
    async def _runner() -> IngestionStats:
        async with db_factory() as session:
            return await seed_geo_data(session, reset_first=reset_first)

    return asyncio.run(_runner())
