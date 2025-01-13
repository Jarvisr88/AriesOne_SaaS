"""Test cases for price utilities."""
import pytest
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.price_models import (
    PriceList,
    PriceItem,
    PriceHistory,
    ICD9Code,
    PriceListCreate,
    PriceListUpdate,
    PriceItemCreate,
    PriceItemUpdate,
    ICD9CodeCreate,
    ICD9CodeUpdate,
    BulkUpdateRequest,
    PriceListType
)
from ..services.price_service import (
    PriceListService,
    PriceItemService,
    ICD9Service
)


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_user():
    """Create mock user."""
    return AsyncMock(
        id=1,
        has_permission=lambda x: True
    )


class TestPriceListService:
    """Test cases for price list service."""
    
    @pytest.mark.asyncio
    async def test_get_price_lists(self, mock_session):
        """Test getting price lists."""
        # Setup
        service = PriceListService(mock_session)
        mock_lists = [
            PriceList(
                id=1,
                name="Default",
                type=PriceListType.DEFAULT
            ),
            PriceList(
                id=2,
                name="Custom",
                type=PriceListType.CUSTOM
            )
        ]
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = mock_lists
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.get_price_lists()
        
        # Verify
        assert len(result) == 2
        assert result[0].name == "Default"
        assert result[1].name == "Custom"
    
    @pytest.mark.asyncio
    async def test_create_price_list(self, mock_session, mock_user):
        """Test creating price list."""
        # Setup
        service = PriceListService(mock_session)
        data = PriceListCreate(
            name="Test List",
            type=PriceListType.DEFAULT,
            effective_date=date.today()
        )
        
        # Execute
        result = await service.create_price_list(data, mock_user.id)
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert result.name == data.name
        assert result.type == data.type
    
    @pytest.mark.asyncio
    async def test_update_price_list(self, mock_session, mock_user):
        """Test updating price list."""
        # Setup
        service = PriceListService(mock_session)
        mock_list = PriceList(
            id=1,
            name="Old Name",
            type=PriceListType.DEFAULT
        )
        update = PriceListUpdate(
            name="New Name",
            type=PriceListType.DEFAULT,
            effective_date=date.today()
        )
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_list
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.update_price_list(1, update, mock_user.id)
        
        # Verify
        assert result.name == "New Name"
        assert mock_session.commit.called


class TestPriceItemService:
    """Test cases for price item service."""
    
    @pytest.mark.asyncio
    async def test_get_items(self, mock_session):
        """Test getting price items."""
        # Setup
        service = PriceItemService(mock_session)
        mock_items = [
            PriceItem(
                id=1,
                billing_code="A1234",
                rent_allowable=Decimal("100.00")
            ),
            PriceItem(
                id=2,
                billing_code="B5678",
                rent_allowable=Decimal("200.00")
            )
        ]
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = mock_items
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.get_items(1)
        
        # Verify
        assert len(result) == 2
        assert result[0].billing_code == "A1234"
        assert result[1].billing_code == "B5678"
    
    @pytest.mark.asyncio
    async def test_update_item(self, mock_session, mock_user):
        """Test updating price item."""
        # Setup
        service = PriceItemService(mock_session)
        mock_item = PriceItem(
            id=1,
            billing_code="A1234",
            rent_allowable=Decimal("100.00"),
            rent_billable=Decimal("90.00"),
            sale_allowable=Decimal("500.00"),
            sale_billable=Decimal("450.00")
        )
        update = PriceItemUpdate(
            billing_code="A1234",
            rent_allowable=Decimal("110.00"),
            rent_billable=Decimal("100.00"),
            sale_allowable=Decimal("550.00"),
            sale_billable=Decimal("500.00"),
            effective_date=date.today(),
            reason="Price increase"
        )
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.update_item(1, update, mock_user.id)
        
        # Verify
        assert result.rent_allowable == Decimal("110.00")
        assert mock_session.add.called  # History record
        assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_bulk_update(self, mock_session, mock_user):
        """Test bulk price update."""
        # Setup
        service = PriceItemService(mock_session)
        request = BulkUpdateRequest(
            items=[
                PriceItemUpdate(
                    id=1,
                    billing_code="A1234",
                    rent_allowable=Decimal("110.00"),
                    rent_billable=Decimal("100.00"),
                    sale_allowable=Decimal("550.00"),
                    sale_billable=Decimal("500.00"),
                    effective_date=date.today()
                ),
                PriceItemUpdate(
                    id=2,
                    billing_code="B5678",
                    rent_allowable=Decimal("210.00"),
                    rent_billable=Decimal("200.00"),
                    sale_allowable=Decimal("650.00"),
                    sale_billable=Decimal("600.00"),
                    effective_date=date.today()
                )
            ],
            update_orders=True
        )
        
        # Mock update_item
        service.update_item = AsyncMock()
        
        # Execute
        result = await service.bulk_update(request, mock_user.id)
        
        # Verify
        assert result.total_items == 2
        assert result.updated_items == 2
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_process_file(self, mock_session, mock_user):
        """Test file processing."""
        # Setup
        service = PriceItemService(mock_session)
        file_content = (
            "billing_code,price\n"
            "A1234,100.00\n"
            "B5678,200.00\n"
        )
        file = AsyncMock(spec=UploadFile)
        file.read = AsyncMock(return_value=file_content.encode())
        file.filename = "prices.csv"
        
        column_map = {
            "billing_code": "billing_code",
            "price": "price"
        }
        
        # Execute
        result = await service.process_file(file, column_map, mock_user.id)
        
        # Verify
        assert result.filename == "prices.csv"
        assert result.total_rows == 2
        assert result.valid_rows == 2
        assert len(result.errors) == 0


class TestICD9Service:
    """Test cases for ICD-9 service."""
    
    @pytest.mark.asyncio
    async def test_get_codes(self, mock_session):
        """Test getting ICD-9 codes."""
        # Setup
        service = ICD9Service(mock_session)
        mock_codes = [
            ICD9Code(
                id=1,
                code="123.45",
                description="Test Code 1"
            ),
            ICD9Code(
                id=2,
                code="678.90",
                description="Test Code 2"
            )
        ]
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = mock_codes
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.get_codes()
        
        # Verify
        assert len(result) == 2
        assert result[0].code == "123.45"
        assert result[1].code == "678.90"
    
    @pytest.mark.asyncio
    async def test_create_code(self, mock_session, mock_user):
        """Test creating ICD-9 code."""
        # Setup
        service = ICD9Service(mock_session)
        data = ICD9CodeCreate(
            code="123.45",
            description="Test Code",
            effective_date=date.today()
        )
        
        # Execute
        result = await service.create_code(data, mock_user.id)
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert result.code == data.code
        assert result.description == data.description
    
    @pytest.mark.asyncio
    async def test_update_code(self, mock_session, mock_user):
        """Test updating ICD-9 code."""
        # Setup
        service = ICD9Service(mock_session)
        mock_code = ICD9Code(
            id=1,
            code="123.45",
            description="Old Description"
        )
        update = ICD9CodeUpdate(
            code="123.45",
            description="New Description",
            effective_date=date.today()
        )
        
        # Mock query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_code
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await service.update_code(1, update, mock_user.id)
        
        # Verify
        assert result.description == "New Description"
        assert mock_session.commit.called
