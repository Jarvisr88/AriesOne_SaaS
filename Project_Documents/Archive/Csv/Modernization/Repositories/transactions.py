"""
Transaction management for CSV import operations.
"""
from typing import Optional, Callable, TypeVar, Any
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..Models.types import ImportStatus

T = TypeVar('T')

class TransactionManager:
    """Manages database transactions for CSV operations."""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @asynccontextmanager
    async def transaction(self) -> Session:
        """Context manager for database transactions."""
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def run_in_transaction(
        self,
        operation: Callable[[Session], T]
    ) -> T:
        """Run an operation within a transaction."""
        async with self.transaction() as session:
            return await operation(session)

    async def run_with_retry(
        self,
        operation: Callable[[Session], T],
        max_retries: int = 3
    ) -> T:
        """Run an operation with retry on failure."""
        retries = 0
        last_error = None

        while retries < max_retries:
            try:
                return await self.run_in_transaction(operation)
            except SQLAlchemyError as e:
                last_error = e
                retries += 1
                # Add exponential backoff here if needed
                continue

        raise last_error

    @asynccontextmanager
    async def import_transaction(
        self,
        import_id: int,
        error_status: ImportStatus = ImportStatus.FAILED
    ):
        """Context manager for import operations with error handling."""
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            # Update import status to error
            try:
                from ..Services.service import CsvService
                service = CsvService(session)
                await service.update_import_status(
                    import_id,
                    error_status,
                    error_message=str(e)
                )
                await session.commit()
            except:
                pass
            raise
        finally:
            await session.close()

    async def run_in_chunks(
        self,
        operation: Callable[[Session, Any], None],
        items: list,
        chunk_size: int = 1000
    ):
        """Run an operation in chunks to handle large datasets."""
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            await self.run_in_transaction(
                lambda session: operation(session, chunk)
            )

    @asynccontextmanager
    async def savepoint(self, session: Session, name: Optional[str] = None):
        """Create a savepoint within a transaction."""
        if not session.in_transaction():
            raise ValueError("No transaction in progress")

        savepoint = await session.begin_nested()
        try:
            yield savepoint
        except:
            await savepoint.rollback()
            raise
        else:
            await savepoint.commit()

    async def execute_batch(
        self,
        operations: list[Callable[[Session], None]]
    ):
        """Execute multiple operations in a single transaction."""
        async with self.transaction() as session:
            for operation in operations:
                await operation(session)

    @asynccontextmanager
    async def lock_import(self, session: Session, import_id: int):
        """Acquire a lock on an import record."""
        # Implementation depends on database type
        # This is a placeholder for row-level locking
        query = f"SELECT * FROM csv_imports WHERE id = {import_id} FOR UPDATE"
        try:
            await session.execute(query)
            yield
        finally:
            # Lock is automatically released at transaction end
            pass
