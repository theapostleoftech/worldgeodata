from app.schemas.common import ORMModel


class CountryOut(ORMModel):
    id: int
    name: str
    iso2: str
    iso3: str
    phone_code: str | None = None
    capital: str | None = None
    currency: str | None = None
    latitude: float | None = None
    longitude: float | None = None
