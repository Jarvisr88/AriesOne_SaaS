"""
Base Repository Module
Provides base class for repositories.
"""
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    """Base repository class."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize base repository.
        
        Args:
            session: Database session
        """
        self.session = session
