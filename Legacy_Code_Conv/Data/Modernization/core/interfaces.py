"""
Interface definitions for the database abstraction layer.
These interfaces define the contract that all database implementations must follow.
"""
from typing import Any, Generic, List, Optional, Protocol, TypeVar
from datetime import datetime

T = TypeVar('T')

class IDatabase(Protocol):
    """Interface for database operations."""
    
    async def connect(self) -> None:
        """Establish database connection."""
        ...

    async def disconnect(self) -> None:
        """Close database connection."""
        ...

    async def health_check(self) -> bool:
        """Check database connection health."""
        ...

    async def begin_transaction(self) -> Any:
        """Start a new transaction."""
        ...

    async def commit_transaction(self, transaction: Any) -> None:
        """Commit an existing transaction."""
        ...

    async def rollback_transaction(self, transaction: Any) -> None:
        """Rollback an existing transaction."""
        ...

class IRepository(Protocol, Generic[T]):
    """Interface for repository pattern implementation."""
    
    async def create(self, **kwargs) -> T:
        """Create a new record."""
        ...

    async def get(self, id: Any) -> Optional[T]:
        """Retrieve a record by ID."""
        ...

    async def update(self, id: Any, **kwargs) -> Optional[T]:
        """Update an existing record."""
        ...

    async def delete(self, id: Any) -> bool:
        """Delete a record."""
        ...

    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List records with pagination."""
        ...

class IAuditableEntity(Protocol):
    """Interface for entities that require audit tracking."""
    
    id: Any
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class IUnitOfWork(Protocol):
    """Interface for Unit of Work pattern implementation."""
    
    async def begin(self) -> None:
        """Begin a new unit of work."""
        ...

    async def commit(self) -> None:
        """Commit the current unit of work."""
        ...

    async def rollback(self) -> None:
        """Rollback the current unit of work."""
        ...

    async def __aenter__(self) -> 'IUnitOfWork':
        """Enter the context manager."""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        ...
