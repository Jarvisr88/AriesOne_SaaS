"""Unit of Work interface module."""
from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from core.interfaces.repository import IRepository

class IUnitOfWork(Protocol):
    """Unit of Work interface for managing transactions."""

    session: AsyncSession

    async def __aenter__(self) -> "IUnitOfWork":
        """Enter the context manager."""
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        raise NotImplementedError

    async def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError

    def get_repository(self, model_type: type) -> IRepository:
        """Get repository for model type.
        
        Args:
            model_type: SQLAlchemy model class.
            
        Returns:
            Repository instance.
        """
        raise NotImplementedError
