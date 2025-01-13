"""Price utilities services."""
from datetime import date, datetime
from decimal import Decimal
import csv
from io import StringIO
from typing import Dict, List, Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.price_models import (
    PriceList,
    PriceItem,
    PriceHistory,
    ICD9Code,
    BulkUpdateRequest,
    BulkUpdateResponse,
    FileUploadResponse,
    PriceListCreate,
    PriceListUpdate,
    PriceItemCreate,
    PriceItemUpdate,
    ICD9CodeCreate,
    ICD9CodeUpdate
)


class PriceListService:
    """Price list service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_price_lists(
        self,
        active_only: bool = True
    ) -> List[PriceList]:
        """Get all price lists.
        
        Args:
            active_only: Only return active lists
            
        Returns:
            List of price lists
        """
        query = select(PriceList)
        if active_only:
            query = query.where(PriceList.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_price_list(self, list_id: int) -> Optional[PriceList]:
        """Get price list by ID.
        
        Args:
            list_id: Price list ID
            
        Returns:
            Price list if found
        """
        query = select(PriceList).where(PriceList.id == list_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_price_list(
        self,
        data: PriceListCreate,
        user_id: int
    ) -> PriceList:
        """Create new price list.
        
        Args:
            data: Price list data
            user_id: Creating user ID
            
        Returns:
            Created price list
            
        Raises:
            HTTPException: If validation fails
        """
        price_list = PriceList(
            **data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.session.add(price_list)
        await self.session.commit()
        return price_list
    
    async def update_price_list(
        self,
        list_id: int,
        data: PriceListUpdate,
        user_id: int
    ) -> PriceList:
        """Update price list.
        
        Args:
            list_id: Price list ID
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated price list
            
        Raises:
            HTTPException: If not found
        """
        price_list = await self.get_price_list(list_id)
        if not price_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price list not found"
            )
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(price_list, key, value)
        
        price_list.updated_by = user_id
        await self.session.commit()
        return price_list


class PriceItemService:
    """Price item service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_items(
        self,
        list_id: int,
        active_only: bool = True
    ) -> List[PriceItem]:
        """Get price items.
        
        Args:
            list_id: Price list ID
            active_only: Only return active items
            
        Returns:
            List of price items
        """
        query = select(PriceItem).where(
            PriceItem.price_list_id == list_id
        )
        if active_only:
            query = query.where(PriceItem.end_date == None)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_item(
        self,
        data: PriceItemCreate,
        user_id: int
    ) -> PriceItem:
        """Create price item.
        
        Args:
            data: Item data
            user_id: Creating user ID
            
        Returns:
            Created item
            
        Raises:
            HTTPException: If validation fails
        """
        item = PriceItem(
            **data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.session.add(item)
        await self.session.commit()
        return item
    
    async def update_item(
        self,
        item_id: int,
        data: PriceItemUpdate,
        user_id: int
    ) -> PriceItem:
        """Update price item.
        
        Args:
            item_id: Item ID
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated item
            
        Raises:
            HTTPException: If not found
        """
        query = select(PriceItem).where(PriceItem.id == item_id)
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price item not found"
            )
        
        # Create history record
        history = PriceHistory(
            price_item_id=item.id,
            rent_allowable=item.rent_allowable,
            rent_billable=item.rent_billable,
            sale_allowable=item.sale_allowable,
            sale_billable=item.sale_billable,
            effective_date=item.effective_date,
            end_date=data.effective_date,
            created_by=user_id,
            reason=data.reason
        )
        self.session.add(history)
        
        # Update item
        for key, value in data.dict(exclude={'reason'}).items():
            setattr(item, key, value)
        
        item.updated_by = user_id
        await self.session.commit()
        return item
    
    async def bulk_update(
        self,
        data: BulkUpdateRequest,
        user_id: int
    ) -> BulkUpdateResponse:
        """Bulk update prices.
        
        Args:
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Update results
        """
        errors = []
        warnings = []
        updated = 0
        
        for item_data in data.items:
            try:
                await self.update_item(
                    item_data.id,
                    item_data,
                    user_id
                )
                updated += 1
            except HTTPException as e:
                errors.append(f"Item {item_data.id}: {str(e.detail)}")
            except Exception as e:
                errors.append(f"Item {item_data.id}: {str(e)}")
        
        return BulkUpdateResponse(
            total_items=len(data.items),
            updated_items=updated,
            errors=errors,
            warnings=warnings
        )
    
    async def process_file(
        self,
        file: UploadFile,
        column_map: Dict[str, str],
        user_id: int
    ) -> FileUploadResponse:
        """Process price file.
        
        Args:
            file: Uploaded file
            column_map: Column mapping
            user_id: Processing user ID
            
        Returns:
            Processing results
            
        Raises:
            HTTPException: If file invalid
        """
        content = await file.read()
        text = content.decode('utf-8')
        
        try:
            reader = csv.DictReader(StringIO(text))
            rows = list(reader)
        except csv.Error as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format: {str(e)}"
            )
        
        errors = []
        warnings = []
        valid_rows = 0
        
        for row in rows:
            try:
                mapped_row = {
                    new_key: row[old_key]
                    for new_key, old_key in column_map.items()
                }
                # Validate row here
                valid_rows += 1
            except KeyError as e:
                errors.append(f"Missing column: {str(e)}")
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
        
        return FileUploadResponse(
            filename=file.filename,
            total_rows=len(rows),
            valid_rows=valid_rows,
            errors=errors,
            warnings=warnings
        )


class ICD9Service:
    """ICD-9 code service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_codes(
        self,
        active_only: bool = True
    ) -> List[ICD9Code]:
        """Get ICD-9 codes.
        
        Args:
            active_only: Only return active codes
            
        Returns:
            List of codes
        """
        query = select(ICD9Code)
        if active_only:
            query = query.where(ICD9Code.end_date == None)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_code(
        self,
        data: ICD9CodeCreate,
        user_id: int
    ) -> ICD9Code:
        """Create ICD-9 code.
        
        Args:
            data: Code data
            user_id: Creating user ID
            
        Returns:
            Created code
            
        Raises:
            HTTPException: If validation fails
        """
        code = ICD9Code(
            **data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.session.add(code)
        await self.session.commit()
        return code
    
    async def update_code(
        self,
        code_id: int,
        data: ICD9CodeUpdate,
        user_id: int
    ) -> ICD9Code:
        """Update ICD-9 code.
        
        Args:
            code_id: Code ID
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated code
            
        Raises:
            HTTPException: If not found
        """
        query = select(ICD9Code).where(ICD9Code.id == code_id)
        result = await self.session.execute(query)
        code = result.scalar_one_or_none()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ICD-9 code not found"
            )
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(code, key, value)
        
        code.updated_by = user_id
        await self.session.commit()
        return code
