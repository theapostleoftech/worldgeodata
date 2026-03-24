from app.schemas.common import ORMModel


class DivisionOut(ORMModel):
    id: int
    name: str
    level: int
    type: str
    parent_id: int | None = None
    country_id: int
    latitude: float | None = None
    longitude: float | None = None
"""Pydantic schemas for administrative divisions."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CountryBase(BaseModel):
    """Base country schema."""

    name: str
    iso2: str
    iso3: str
    phone_code: Optional[str] = None
    capital: Optional[str] = None
    currency: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CountryCreate(CountryBase):
    """Create country schema."""

    pass


class CountryUpdate(BaseModel):
    """Update country schema."""

    name: Optional[str] = None
    capital: Optional[str] = None
    currency: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CountryResponse(CountryBase):
    """Country response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDivisionBase(BaseModel):
    """Base admin division schema."""

    name: str
    level: int
    type: str
    country_id: int
    parent_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AdminDivisionCreate(AdminDivisionBase):
    """Create admin division schema."""

    pass


class AdminDivisionUpdate(BaseModel):
    """Update admin division schema."""

    name: Optional[str] = None
    parent_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AdminDivisionResponse(AdminDivisionBase):
    """Admin division response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDivisionWithChildren(AdminDivisionResponse):
    """Admin division with children schema."""

    children: list["AdminDivisionResponse"] = []


class CityBase(BaseModel):
    """Base city schema."""

    name: str
    country_id: int
    admin_division_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    is_capital: int = 0


class CityCreate(CityBase):
    """Create city schema."""

    pass


class CityUpdate(BaseModel):
    """Update city schema."""

    name: Optional[str] = None
    admin_division_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None


class CityResponse(CityBase):
    """City response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Recursive model update
AdminDivisionWithChildren.model_rebuild()
