"""
ICD Codes Repository Module
Version: 1.0.0
Last Updated: 2025-01-12

This module provides repository implementations for ICD code related models.
"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload

from .base import SQLAlchemyRepository
from ..models.icd_codes import ICDCode, ICDCodeMapping

class ICDCodeRepository(SQLAlchemyRepository[ICDCode]):
    """Repository for managing ICD codes."""
    
    def __init__(self, session: Session):
        super().__init__(session, ICDCode)
    
    def get_by_code(self, code: str) -> Optional[ICDCode]:
        """Get ICD code by its code value."""
        stmt = select(ICDCode).where(ICDCode.code == code)
        return self._session.execute(stmt).scalar_one_or_none()
    
    def get_active_codes(self, version: Optional[str] = None) -> List[ICDCode]:
        """Get all active ICD codes, optionally filtered by version."""
        stmt = select(ICDCode).where(
            and_(
                ICDCode.is_active == True,
                or_(
                    ICDCode.end_date.is_(None),
                    ICDCode.end_date > datetime.utcnow()
                )
            )
        )
        if version:
            stmt = stmt.where(ICDCode.version == version)
        return list(self._session.execute(stmt).scalars().all())
    
    def get_codes_by_price_list_item(self, item_id: int) -> List[ICDCode]:
        """Get all ICD codes associated with a price list item."""
        stmt = select(ICDCode).join(
            ICDCode.price_list_items
        ).where(
            ICDCode.price_list_items.any(id=item_id)
        )
        return list(self._session.execute(stmt).scalars().all())

class ICDCodeMappingRepository(SQLAlchemyRepository[ICDCodeMapping]):
    """Repository for managing ICD code mappings."""
    
    def __init__(self, session: Session):
        super().__init__(session, ICDCodeMapping)
    
    def get_mappings_by_source(self, source_code_id: int) -> List[ICDCodeMapping]:
        """Get all mappings for a source ICD code."""
        stmt = select(ICDCodeMapping).options(
            joinedload(ICDCodeMapping.target_code)
        ).where(
            and_(
                ICDCodeMapping.source_code_id == source_code_id,
                ICDCodeMapping.is_active == True,
                or_(
                    ICDCodeMapping.end_date.is_(None),
                    ICDCodeMapping.end_date > datetime.utcnow()
                )
            )
        )
        return list(self._session.execute(stmt).scalars().all())
    
    def get_mapping(self, source_code_id: int, target_code_id: int) -> Optional[ICDCodeMapping]:
        """Get specific mapping between two ICD codes."""
        stmt = select(ICDCodeMapping).where(
            and_(
                ICDCodeMapping.source_code_id == source_code_id,
                ICDCodeMapping.target_code_id == target_code_id,
                ICDCodeMapping.is_active == True
            )
        )
        return self._session.execute(stmt).scalar_one_or_none()
    
    def get_active_mappings_by_version(self, source_version: str, target_version: str) -> List[ICDCodeMapping]:
        """Get all active mappings between two ICD versions."""
        stmt = select(ICDCodeMapping).join(
            ICDCodeMapping.source_code
        ).join(
            ICDCodeMapping.target_code
        ).where(
            and_(
                ICDCode.version == source_version,
                ICDCode.version == target_version,
                ICDCodeMapping.is_active == True,
                or_(
                    ICDCodeMapping.end_date.is_(None),
                    ICDCodeMapping.end_date > datetime.utcnow()
                )
            )
        )
        return list(self._session.execute(stmt).scalars().all())
