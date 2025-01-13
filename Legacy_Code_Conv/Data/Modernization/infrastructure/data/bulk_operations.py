"""Bulk operations module for efficient batch processing."""
from typing import List, Type, TypeVar
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert

from infrastructure.database.base import Base

T = TypeVar('T', bound=Base)

class BulkOperations:
    """Bulk operations handler for efficient batch processing."""

    def __init__(self, session: AsyncSession):
        """Initialize bulk operations.
        
        Args:
            session: Database session.
        """
        self._session = session

    async def bulk_insert(self, model: Type[T], items: List[dict]) -> None:
        """Bulk insert items.
        
        Args:
            model: SQLAlchemy model class.
            items: List of items to insert.
        """
        if not items:
            return

        stmt = insert(model).values(items)
        await self._session.execute(stmt)

    async def bulk_update(
        self,
        model: Type[T],
        items: List[dict],
        key_fields: List[str]
    ) -> None:
        """Bulk update items.
        
        Args:
            model: SQLAlchemy model class.
            items: List of items to update.
            key_fields: Fields to use as update keys.
        """
        if not items:
            return

        # Create WHERE clause for matching records
        where_clause = []
        for key in key_fields:
            where_clause.append(getattr(model, key) == items[0][key])

        stmt = update(model).where(*where_clause).values(items)
        await self._session.execute(stmt)

    async def bulk_delete(
        self,
        model: Type[T],
        filters: List[dict]
    ) -> None:
        """Bulk delete items.
        
        Args:
            model: SQLAlchemy model class.
            filters: List of filter conditions.
        """
        if not filters:
            return

        # Create WHERE clause from filters
        where_clause = []
        for filter_dict in filters:
            for key, value in filter_dict.items():
                where_clause.append(getattr(model, key) == value)

        stmt = delete(model).where(*where_clause)
        await self._session.execute(stmt)

    async def bulk_upsert(
        self,
        model: Type[T],
        items: List[dict],
        key_fields: List[str],
        update_fields: List[str]
    ) -> None:
        """Bulk upsert (insert or update) items.
        
        Args:
            model: SQLAlchemy model class.
            items: List of items to upsert.
            key_fields: Fields to use as upsert keys.
            update_fields: Fields to update on conflict.
        """
        if not items:
            return

        # Create the upsert statement
        stmt = upsert(model).values(items)

        # Specify the conflict target (key fields)
        update_dict = {
            field: stmt.excluded[field]
            for field in update_fields
        }

        # Add the DO UPDATE clause
        stmt = stmt.on_conflict_do_update(
            index_elements=key_fields,
            set_=update_dict
        )

        await self._session.execute(stmt)
