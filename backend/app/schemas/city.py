from app.schemas.common import ORMModel


class CityOut(ORMModel):
    id: int
    name: str
    admin_division_id: int | None = None
    country_id: int
    latitude: float | None = None
    longitude: float | None = None
