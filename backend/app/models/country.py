from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Country(Base, TimestampMixin):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    phone_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    capital: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)

    divisions = relationship("AdminDivision", back_populates="country", cascade="all, delete-orphan")
    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_countries_name_iso2", "name", "iso2"),)
