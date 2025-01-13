from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.core.logging import logger
from app.repositories.medicare import (
    BeneficiaryRepository,
    ClaimRepository,
    ProviderRepository,
    EligibilityCheckRepository
)

class UnitOfWork:
    def __init__(self):
        self.session: Optional[AsyncSession] = None
        self._repositories = {}

    async def __aenter__(self) -> "UnitOfWork":
        self.session = async_session()
        
        # Initialize repositories
        self._repositories = {
            "beneficiary": BeneficiaryRepository(self.session),
            "claim": ClaimRepository(self.session),
            "provider": ProviderRepository(self.session),
            "eligibility": EligibilityCheckRepository(self.session)
        }
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            try:
                await self.commit()
            except Exception as e:
                await self.rollback()
                logger.error(f"Transaction rolled back due to commit error: {e}")
                raise
        
        await self.session.close()

    async def commit(self):
        """Commit the current transaction"""
        if self.session:
            try:
                await self.session.commit()
            except Exception as e:
                logger.error(f"Error committing transaction: {e}")
                raise

    async def rollback(self):
        """Rollback the current transaction"""
        if self.session:
            try:
                await self.session.rollback()
            except Exception as e:
                logger.error(f"Error rolling back transaction: {e}")
                raise

    def __getattr__(self, name: str):
        """Get repository by name"""
        if name in self._repositories:
            return self._repositories[name]
        raise AttributeError(f"Repository {name} not found")

@asynccontextmanager
async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Get a unit of work instance"""
    async with UnitOfWork() as uow:
        try:
            yield uow
        except Exception as e:
            logger.error(f"Error in unit of work: {e}")
            raise

class TransactionContext:
    """Context manager for handling transactions"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __aenter__(self):
        return self.uow

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.uow.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
            raise
        try:
            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            logger.error(f"Transaction rolled back due to commit error: {e}")
            raise

async def in_transaction(uow: UnitOfWork):
    """Decorator for handling transactions"""
    return TransactionContext(uow)
