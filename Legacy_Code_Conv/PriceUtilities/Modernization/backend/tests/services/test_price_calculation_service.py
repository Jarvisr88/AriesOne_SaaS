"""
Tests for PriceCalculationService
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from ...src.services.price_calculation_service import PriceCalculationService
from ...src.models.price_list import PriceList
from ...src.models.parameters import Parameter
from ...src.models.icd_codes import ICDCode

@pytest.fixture
def mock_repos():
    """Create mock repositories"""
    price_list_repo = Mock()
    parameter_repo = Mock()
    icd_code_repo = Mock()
    return price_list_repo, parameter_repo, icd_code_repo

@pytest.fixture
def service(mock_repos):
    """Create service instance with mock repos"""
    price_list_repo, parameter_repo, icd_code_repo = mock_repos
    return PriceCalculationService(
        price_list_repo=price_list_repo,
        parameter_repo=parameter_repo,
        icd_code_repo=icd_code_repo
    )

def test_calculate_price_basic(service, mock_repos):
    """Test basic price calculation without modifiers"""
    price_list_repo, _, _ = mock_repos
    
    # Setup mock data
    price_list_repo.get_by_id.return_value = PriceList(
        item_id="TEST001",
        base_price=Decimal("100.00"),
        currency="USD"
    )
    
    # Calculate price
    result = service.calculate_price(
        item_id="TEST001",
        quantity=1,
        icd_codes=[]
    )
    
    # Verify results
    assert result["base_price"] == Decimal("100.00")
    assert result["final_price"] == Decimal("100.00")
    assert result["currency"] == "USD"

def test_calculate_price_with_quantity_discount(service, mock_repos):
    """Test price calculation with quantity discounts"""
    price_list_repo, _, _ = mock_repos
    
    # Setup mock data
    price_list_repo.get_by_id.return_value = PriceList(
        item_id="TEST001",
        base_price=Decimal("100.00"),
        currency="USD",
        quantity_breaks={
            10: Decimal("0.10"),  # 10% discount for 10+ items
            20: Decimal("0.20")   # 20% discount for 20+ items
        }
    )
    
    # Calculate prices for different quantities
    result_small = service.calculate_price(
        item_id="TEST001",
        quantity=5,
        icd_codes=[]
    )
    
    result_medium = service.calculate_price(
        item_id="TEST001",
        quantity=15,
        icd_codes=[]
    )
    
    result_large = service.calculate_price(
        item_id="TEST001",
        quantity=25,
        icd_codes=[]
    )
    
    # Verify results
    assert result_small["final_price"] == Decimal("500.00")  # No discount
    assert result_medium["final_price"] == Decimal("1350.00")  # 10% discount
    assert result_large["final_price"] == Decimal("2000.00")  # 20% discount

def test_calculate_price_with_icd_modifiers(service, mock_repos):
    """Test price calculation with ICD code modifiers"""
    price_list_repo, _, icd_code_repo = mock_repos
    
    # Setup mock data
    price_list_repo.get_by_id.return_value = PriceList(
        item_id="TEST001",
        base_price=Decimal("100.00"),
        currency="USD"
    )
    
    icd_code_repo.get_by_code.side_effect = lambda code: {
        "ICD1": ICDCode(code="ICD1", price_modifier=Decimal("1.1")),  # 10% increase
        "ICD2": ICDCode(code="ICD2", price_modifier=Decimal("0.9"))   # 10% decrease
    }.get(code)
    
    # Calculate price with ICD codes
    result = service.calculate_price(
        item_id="TEST001",
        quantity=1,
        icd_codes=["ICD1", "ICD2"]
    )
    
    # Verify results (1.1 * 0.9 = 0.99)
    assert result["final_price"] == Decimal("99.00")

def test_calculate_price_with_parameters(service, mock_repos):
    """Test price calculation with date parameters"""
    price_list_repo, parameter_repo, _ = mock_repos
    test_date = datetime(2025, 1, 1)
    
    # Setup mock data
    price_list_repo.get_by_id.return_value = PriceList(
        item_id="TEST001",
        base_price=Decimal("100.00"),
        currency="USD"
    )
    
    parameter_repo.get_active_parameters.return_value = [
        Parameter(
            name="SEASONAL_MODIFIER",
            value=Decimal("1.2"),
            parameter_type="MULTIPLIER"
        ),
        Parameter(
            name="FIXED_FEE",
            value=Decimal("10.00"),
            parameter_type="FIXED_ADDITION"
        )
    ]
    
    # Calculate price with parameters
    result = service.calculate_price(
        item_id="TEST001",
        quantity=1,
        icd_codes=[],
        date=test_date
    )
    
    # Verify results (100 * 1.2 + 10 = 130)
    assert result["final_price"] == Decimal("130.00")

def test_calculate_price_item_not_found(service, mock_repos):
    """Test price calculation with non-existent item"""
    price_list_repo, _, _ = mock_repos
    price_list_repo.get_by_id.return_value = None
    
    # Verify exception is raised
    with pytest.raises(ValueError, match="Item TEST001 not found"):
        service.calculate_price(
            item_id="TEST001",
            quantity=1,
            icd_codes=[]
        )

def test_calculate_price_invalid_quantity(service, mock_repos):
    """Test price calculation with invalid quantity"""
    price_list_repo, _, _ = mock_repos
    
    # Setup mock data
    price_list_repo.get_by_id.return_value = PriceList(
        item_id="TEST001",
        base_price=Decimal("100.00"),
        currency="USD"
    )
    
    # Verify exception is raised for zero quantity
    with pytest.raises(ValueError, match="Quantity must be positive"):
        service.calculate_price(
            item_id="TEST001",
            quantity=0,
            icd_codes=[]
        )
    
    # Verify exception is raised for negative quantity
    with pytest.raises(ValueError, match="Quantity must be positive"):
        service.calculate_price(
            item_id="TEST001",
            quantity=-1,
            icd_codes=[]
        )
