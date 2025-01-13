"""
Base model configuration for SQLAlchemy models.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import Any, Dict

Base = declarative_base()

class ModelMixin:
    """Mixin class to add common functionality to all models."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create model instance from dictionary."""
        return cls(**{
            k: v for k, v in data.items() 
            if k in cls.__table__.columns.keys()
        })
    
    def update(self, session: Session, **kwargs) -> None:
        """Update model instance with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.add(self)
        session.commit()

# Add ModelMixin to Base
Base.to_dict = ModelMixin.to_dict
Base.from_dict = classmethod(ModelMixin.from_dict)
Base.update = ModelMixin.update
