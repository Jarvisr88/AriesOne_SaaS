"""Company model module.

This module defines the Company model which represents healthcare organizations in the system.
Companies are the top-level entities that own locations, sessions, and other resources.

Attributes:
    Base: SQLAlchemy declarative base class
    TimestampMixin: Adds created_at and updated_at fields
    SoftDeleteMixin: Adds is_deleted and deleted_at fields

Example:
    Creating a new company:
    ```python
    company = Company(
        name="Acme Healthcare",
        tax_id="12-3456789",
        npi="1234567890",
        is_active=True
    )
    ```
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime

from infrastructure.database.base import Base, TimestampMixin, SoftDeleteMixin

class Company(Base, TimestampMixin, SoftDeleteMixin):
    """Company model representing healthcare organizations.
    
    This class represents a healthcare company in the system. Each company can have
    multiple locations and sessions. Companies are identified by their unique NPI
    (National Provider Identifier) and tax ID.
    
    Attributes:
        id (UUID): Primary key, auto-generated UUID4
        name (str): Company name, max length 255 chars
        tax_id (str): Unique tax identification number, max length 50 chars
        npi (str): National Provider Identifier, unique 10-digit number
        is_active (bool): Whether the company is currently active
        license_expiry (datetime, optional): When the company's license expires
        address (str, optional): Physical address, max length 500 chars
        phone (str, optional): Contact phone number, max length 20 chars
        email (str, optional): Contact email, max length 255 chars
        website (str, optional): Company website URL, max length 255 chars
        locations (List[Location]): List of company locations
        sessions (List[Session]): List of company sessions
    
    Properties:
        is_license_valid (bool): Whether the company's license is currently valid
        active_locations (List[Location]): List of active company locations
    
    Note:
        - NPI must be exactly 10 digits
        - Tax ID should be in format XX-XXXXXXX
        - Company is soft-deletable (marked as deleted rather than removed)
        - All timestamps are stored in UTC
    """

    __tablename__ = "companies"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        doc="Unique identifier for the company"
    )
    
    # Required fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Company name"
    )
    tax_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        doc="Tax identification number (format: XX-XXXXXXX)"
    )
    npi: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        doc="National Provider Identifier (10 digits)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the company is currently active"
    )
    
    # Optional fields
    license_expiry: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the company's license expires"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Physical address"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Contact phone number"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Contact email address"
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(255),
        doc="Company website URL"
    )
    
    # Relationships
    locations = relationship(
        "Location",
        back_populates="company",
        doc="Company locations"
    )
    sessions = relationship(
        "Session",
        back_populates="company",
        doc="Company sessions"
    )
    
    @property
    def is_license_valid(self) -> bool:
        """Check if company's license is currently valid.
        
        Returns:
            bool: True if license is valid (not expired), False otherwise
        """
        if not self.license_expiry:
            return False
        return datetime.utcnow() < self.license_expiry
    
    @property
    def active_locations(self) -> List["Location"]:
        """Get list of active locations for this company.
        
        Returns:
            List[Location]: List of active company locations
        """
        return [loc for loc in self.locations if loc.is_active]
    
    def __repr__(self) -> str:
        """Get string representation of Company.
        
        Returns:
            str: String representation including ID, name, and NPI
        """
        return f"Company(id={self.id}, name={self.name}, npi={self.npi})"
