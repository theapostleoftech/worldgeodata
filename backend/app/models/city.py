from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class City(Base, TimestampMixin):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    admin_division_id: Mapped[int | None] = mapped_column(ForeignKey("admin_divisions.id"), index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), index=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)

    admin_division = relationship("AdminDivision", back_populates="cities")
    country = relationship("Country", back_populates="cities")

    __table_args__ = (Index("ix_cities_country_division_name", "country_id", "admin_division_id", "name"),)
