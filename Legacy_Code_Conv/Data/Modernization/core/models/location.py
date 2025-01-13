"""Location model module."""
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey

from infrastructure.database.base import Base, TimestampMixin, SoftDeleteMixin

class Location(Base, TimestampMixin, SoftDeleteMixin):
    """Location model representing company facilities."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("tbl_company.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    fax: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    company = relationship("Company", back_populates="locations")
    sessions = relationship("Session", back_populates="location")
    
    def __repr__(self) -> str:
        """String representation of Location."""
        return f"Location(id={self.id}, name={self.name}, company_id={self.company_id})"
