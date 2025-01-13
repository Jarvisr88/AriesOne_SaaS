"""
Same or Similar Claims Repository Module
This module provides data access for same or similar claim checks.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.integration_settings_model import IntegrationSettings

class SameOrSimilarRepository:
    """
    Repository for managing same or similar claim data access.
    Handles database operations for NPI, billing codes, and settings.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            session (AsyncSession): Database session
        """
        self.session = session
    
    async def get_npis(self) -> List[Dict[str, str]]:
        """
        Get available NPIs from database.
        
        Returns:
            List[Dict[str, str]]: List of NPI entries
        """
        query = """
            SELECT Npi, State, 'Company' as Description
            FROM tbl_company
            WHERE ID = 1 AND Npi != ''
            UNION ALL
            SELECT Npi, State, Name as Description
            FROM tbl_location
            WHERE Npi != ''
        """
        
        result = await self.session.execute(query)
        return [
            {
                "npi": row.Npi,
                "state": row.State,
                "description": row.Description
            }
            for row in result
        ]
    
    async def get_billing_codes(self) -> List[str]:
        """
        Get available billing codes from database.
        
        Returns:
            List[str]: List of billing codes
        """
        # TODO: Implement actual billing code retrieval
        # This is a placeholder that needs to be implemented
        # based on the specific database schema
        return []
    
    async def get_settings(self) -> Optional[IntegrationSettings]:
        """
        Get integration settings from database.
        
        Returns:
            Optional[IntegrationSettings]: Settings if found
        """
        query = """
            SELECT AbilityIntegrationSettings
            FROM tbl_company
            WHERE ID = 1
        """
        
        result = await self.session.execute(query)
        row = result.first()
        
        if not row or not row.AbilityIntegrationSettings:
            return None
            
        return IntegrationSettings.from_xml(row.AbilityIntegrationSettings)
    
    async def save_settings(self, settings: IntegrationSettings) -> bool:
        """
        Save integration settings to database.
        
        Args:
            settings (IntegrationSettings): Settings to save
            
        Returns:
            bool: True if saved successfully
        """
        query = """
            UPDATE tbl_company
            SET AbilityIntegrationSettings = :settings
            WHERE ID = 1
        """
        
        result = await self.session.execute(
            query,
            {"settings": settings.to_xml()}
        )
        await self.session.commit()
        
        return result.rowcount > 0
