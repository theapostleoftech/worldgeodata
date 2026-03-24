from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AdminDivision(Base, TimestampMixin):
    __tablename__ = "admin_divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    level: Mapped[int] = mapped_column(Integer, index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("admin_divisions.id"), index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), index=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)

    country = relationship("Country", back_populates="divisions")
    parent = relationship("AdminDivision", remote_side=[id], back_populates="children")
    children = relationship("AdminDivision", back_populates="parent", cascade="all, delete-orphan")
    cities = relationship("City", back_populates="admin_division", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_admin_divisions_country_parent", "country_id", "parent_id"),
        Index("ix_admin_divisions_country_level_name", "country_id", "level", "name"),
    )
