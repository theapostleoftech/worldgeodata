from app.schemas.common import ORMModel


class NearbyResultOut(ORMModel):
    entity_type: str
    id: int
    name: str
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float


class ReverseGeocodeOut(ORMModel):
    country: str | None = None
    division_path: list[str] = []
    city: str | None = None
