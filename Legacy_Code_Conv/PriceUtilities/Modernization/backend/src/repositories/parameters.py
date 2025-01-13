"""
Parameters Repository Module
Version: 1.0.0
Last Updated: 2025-01-12

This module provides repository implementations for pricing parameters and rules.
"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload

from .base import SQLAlchemyRepository
from ..models.parameters import PriceParameter, PriceRule, ParameterHistory

class PriceParameterRepository(SQLAlchemyRepository[PriceParameter]):
    """Repository for managing price parameters."""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceParameter)
    
    def get_by_name(self, name: str) -> Optional[PriceParameter]:
        """Get parameter by name."""
        stmt = select(PriceParameter).where(PriceParameter.name == name)
        return self._session.execute(stmt).scalar_one_or_none()
    
    def get_active_parameters(self) -> List[PriceParameter]:
        """Get all active parameters."""
        stmt = select(PriceParameter).where(
            and_(
                PriceParameter.is_active == True,
                or_(
                    PriceParameter.end_date.is_(None),
                    PriceParameter.end_date > datetime.utcnow()
                )
            )
        )
        return list(self._session.execute(stmt).scalars().all())
    
    def update_parameter_value(self, id: int, new_value: float, reason: str) -> Optional[PriceParameter]:
        """Update parameter value with history tracking."""
        parameter = self.get(id)
        if parameter:
            # Create parameter history
            history = ParameterHistory(
                parameter_id=parameter.id,
                previous_value=parameter.value,
                new_value=new_value,
                change_reason=reason,
                change_type='manual',
                previous_config=parameter.config,
                new_config=parameter.config
            )
            self._session.add(history)
            
            # Update parameter
            parameter.value = new_value
            self._session.commit()
            self._session.refresh(parameter)
            return parameter
        return None

class PriceRuleRepository(SQLAlchemyRepository[PriceRule]):
    """Repository for managing price rules."""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceRule)
    
    def get_active_rules_by_parameter(self, parameter_id: int) -> List[PriceRule]:
        """Get all active rules for a parameter."""
        stmt = select(PriceRule).where(
            and_(
                PriceRule.parameter_id == parameter_id,
                PriceRule.is_active == True
            )
        ).order_by(PriceRule.priority.desc())
        return list(self._session.execute(stmt).scalars().all())
    
    def get_rules_by_type(self, rule_type: str) -> List[PriceRule]:
        """Get all rules of a specific type."""
        stmt = select(PriceRule).where(
            and_(
                PriceRule.rule_type == rule_type,
                PriceRule.is_active == True
            )
        ).order_by(PriceRule.priority.desc())
        return list(self._session.execute(stmt).scalars().all())

class ParameterHistoryRepository(SQLAlchemyRepository[ParameterHistory]):
    """Repository for managing parameter history."""
    
    def __init__(self, session: Session):
        super().__init__(session, ParameterHistory)
    
    def get_parameter_history(self, parameter_id: int) -> List[ParameterHistory]:
        """Get history for a specific parameter."""
        stmt = select(ParameterHistory).where(
            ParameterHistory.parameter_id == parameter_id
        ).order_by(ParameterHistory.change_date.desc())
        return list(self._session.execute(stmt).scalars().all())
