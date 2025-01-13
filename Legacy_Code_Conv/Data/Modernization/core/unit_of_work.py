"""
Unit of Work pattern implementation for managing database transactions.
Ensures data consistency across multiple repository operations.
"""
from typing import Dict, Type
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import logging
from .database import Database, Repository
from .interfaces import IUnitOfWork

class UnitOfWork(IUnitOfWork):
    """Implements the Unit of Work pattern for managing database transactions."""

    def __init__(self, db: Database):
        self.db = db
        self._repositories: Dict[Type, Repository] = {}
        self.logger = logging.getLogger(__name__)

    def repository(self, model_type: Type) -> Repository:
        """Get or create a repository for the given model type."""
        if model_type not in self._repositories:
            self._repositories[model_type] = Repository(self.db, model_type)
        return self._repositories[model_type]

    async def begin(self) -> None:
        """Begin a new database transaction."""
        self.session = self.db.async_session()
        self.logger.debug("Started new database transaction")

    async def commit(self) -> None:
        """Commit the current transaction."""
        try:
            await self.session.commit()
            self.logger.debug("Committed database transaction")
        except Exception as e:
            self.logger.error(f"Failed to commit transaction: {str(e)}")
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        try:
            await self.session.rollback()
            self.logger.debug("Rolled back database transaction")
        except Exception as e:
            self.logger.error(f"Failed to rollback transaction: {str(e)}")
            raise

    async def __aenter__(self) -> 'UnitOfWork':
        """Enter the context manager."""
        await self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

@asynccontextmanager
async def unit_of_work(db: Database):
    """Context manager for database transactions."""
    async with UnitOfWork(db) as uow:
        yield uow
