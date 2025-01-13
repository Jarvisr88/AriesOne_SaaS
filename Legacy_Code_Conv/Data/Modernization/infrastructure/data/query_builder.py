"""Query builder module for constructing complex queries."""
from typing import Any, List, Optional, Type, TypeVar
from sqlalchemy import Select, select, and_, or_, desc, asc
from sqlalchemy.sql.expression import BinaryExpression

from infrastructure.database.base import Base

T = TypeVar('T', bound=Base)

class QueryBuilder:
    """Builder for constructing complex SQLAlchemy queries."""

    def __init__(self, model: Type[T]):
        """Initialize query builder.
        
        Args:
            model: SQLAlchemy model class.
        """
        self._model = model
        self._query: Select = select(model)
        self._filters: List[BinaryExpression] = []
        self._order_by: List[Any] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    def filter(self, *filters: BinaryExpression) -> "QueryBuilder":
        """Add filter conditions.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            Self for chaining.
        """
        self._filters.extend(filters)
        return self

    def filter_by(self, **kwargs: Any) -> "QueryBuilder":
        """Add equality filters.
        
        Args:
            kwargs: Field name and value pairs.
            
        Returns:
            Self for chaining.
        """
        for key, value in kwargs.items():
            self._filters.append(getattr(self._model, key) == value)
        return self

    def or_filter(self, *filters: BinaryExpression) -> "QueryBuilder":
        """Add OR filter conditions.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            Self for chaining.
        """
        self._filters.append(or_(*filters))
        return self

    def order_by(self, *criteria: Any) -> "QueryBuilder":
        """Add ordering criteria.
        
        Args:
            criteria: SQLAlchemy order criteria.
            
        Returns:
            Self for chaining.
        """
        self._order_by.extend(criteria)
        return self

    def order_by_desc(self, *columns: str) -> "QueryBuilder":
        """Add descending order criteria.
        
        Args:
            columns: Column names.
            
        Returns:
            Self for chaining.
        """
        for column in columns:
            self._order_by.append(desc(getattr(self._model, column)))
        return self

    def order_by_asc(self, *columns: str) -> "QueryBuilder":
        """Add ascending order criteria.
        
        Args:
            columns: Column names.
            
        Returns:
            Self for chaining.
        """
        for column in columns:
            self._order_by.append(asc(getattr(self._model, column)))
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set limit.
        
        Args:
            limit: Maximum number of results.
            
        Returns:
            Self for chaining.
        """
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set offset.
        
        Args:
            offset: Number of results to skip.
            
        Returns:
            Self for chaining.
        """
        self._offset = offset
        return self

    def build(self) -> Select:
        """Build the final query.
        
        Returns:
            SQLAlchemy select statement.
        """
        if self._filters:
            self._query = self._query.where(and_(*self._filters))
        
        if self._order_by:
            self._query = self._query.order_by(*self._order_by)
        
        if self._limit is not None:
            self._query = self._query.limit(self._limit)
        
        if self._offset is not None:
            self._query = self._query.offset(self._offset)
        
        return self._query
