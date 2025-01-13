"""Unit of Work implementation module."""
from typing import Dict, Type
from sqlalchemy.ext.asyncio import AsyncSession

from core.interfaces.unit_of_work import IUnitOfWork
from core.interfaces.repository import IRepository
from infrastructure.repositories.base import Repository
from infrastructure.database.base import Base

class UnitOfWork(IUnitOfWork):
    """Unit of Work implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize Unit of Work.
        
        Args:
            session: Database session.
        """
        self.session = session
        self._repositories: Dict[Type[Base], IRepository] = {}

    async def __aenter__(self) -> "UnitOfWork":
        """Enter the context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager.
        
        Commits if no exception occurred, otherwise rolls back.
        """
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()

    def get_repository(self, model_type: Type[Base]) -> IRepository:
        """Get repository for model type.
        
        Creates a new repository if one doesn't exist.
        
        Args:
            model_type: SQLAlchemy model class.
            
        Returns:
            Repository instance.
        """
        if model_type not in self._repositories:
            self._repositories[model_type] = Repository(self.session, model_type)
        return self._repositories[model_type]
