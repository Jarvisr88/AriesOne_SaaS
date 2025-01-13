import pytest
from datetime import datetime, date
from decimal import Decimal
import asyncio
from integration.billing_system import (
    BillingSystemIntegration,
    TransactionCreate,
    PaymentStatus,
    PaymentMethod
)
from unittest.mock import AsyncMock, patch

@pytest.fixture
def billing_system():
    """Create a test instance of BillingSystemIntegration"""
    return BillingSystemIntegration(
        db_url="postgresql://test:test@localhost/test_db",
        api_base_url="https://test.billing.com/v1",
        api_key="test-api-key"
    )

@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing"""
    return TransactionCreate(
        patient_id="P12345",
        provider_id="PR67890",
        service_date=date.today(),
        amount=Decimal("150.00"),
        payment_method=PaymentMethod.CREDIT_CARD,
        reference_number="REF123"
    )

@pytest.mark.asyncio
async def test_create_transaction(billing_system, sample_transaction):
    """Test creating a new billing transaction"""
    # Mock external API call
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": "EXT123",
            "status": "created"
        }

        # Create transaction
        result = await billing_system.create_transaction(sample_transaction)

        # Verify result
        assert result["status"] == "success"
        assert "transaction_id" in result
        assert "external_id" in result
        assert result["external_id"] == "EXT123"

@pytest.mark.asyncio
async def test_process_payment(billing_system):
    """Test processing payment for a transaction"""
    transaction_id = 1
    payment_details = {
        "method": PaymentMethod.CREDIT_CARD,
        "amount": "150.00",
        "card_token": "tok_test123"
    }

    # Mock external API call
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": PaymentStatus.CAPTURED,
            "transaction_id": "EXT123"
        }

        # Process payment
        result = await billing_system.process_payment(transaction_id, payment_details)

        # Verify result
        assert result["status"] == "success"
        assert result["payment_status"] == PaymentStatus.CAPTURED
        assert result["transaction_id"] == transaction_id

@pytest.mark.asyncio
async def test_void_transaction(billing_system):
    """Test voiding a transaction"""
    transaction_id = 1

    # Mock external API call
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "voided"
        }

        # Void transaction
        result = await billing_system.void_transaction(transaction_id)

        # Verify result
        assert result["status"] == "success"
        assert "Transaction voided successfully" in result["message"]
        assert result["transaction_id"] == transaction_id

@pytest.mark.asyncio
async def test_get_transaction_history(billing_system):
    """Test retrieving transaction history"""
    filters = {
        "patient_id": "P12345",
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 12, 31),
        "status": PaymentStatus.CAPTURED
    }

    # Get transaction history
    transactions = await billing_system.get_transaction_history(**filters)

    # Verify result structure
    assert isinstance(transactions, list)
    for transaction in transactions:
        assert "id" in transaction
        assert "patient_id" in transaction
        assert "amount" in transaction
        assert "status" in transaction
        assert "created_at" in transaction

@pytest.mark.asyncio
async def test_error_handling(billing_system, sample_transaction):
    """Test error handling in billing operations"""
    # Test API error
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            await billing_system.create_transaction(sample_transaction)
        assert "API Error" in str(exc_info.value)

    # Test invalid transaction
    invalid_transaction = sample_transaction.copy()
    invalid_transaction.amount = Decimal("-100.00")  # Invalid negative amount

    with pytest.raises(Exception) as exc_info:
        await billing_system.create_transaction(invalid_transaction)
    assert "validation" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_concurrent_transactions(billing_system, sample_transaction):
    """Test handling concurrent transactions"""
    num_transactions = 5
    
    # Create multiple transactions concurrently
    async def create_transaction():
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "id": "EXT123",
                "status": "created"
            }
            return await billing_system.create_transaction(sample_transaction)

    tasks = [create_transaction() for _ in range(num_transactions)]
    results = await asyncio.gather(*tasks)

    # Verify all transactions were created successfully
    assert len(results) == num_transactions
    for result in results:
        assert result["status"] == "success"
        assert "transaction_id" in result

@pytest.mark.asyncio
async def test_transaction_validation(billing_system):
    """Test transaction validation rules"""
    # Test invalid amount
    with pytest.raises(Exception):
        invalid_transaction = TransactionCreate(
            patient_id="P12345",
            provider_id="PR67890",
            service_date=date.today(),
            amount=Decimal("0.00"),  # Invalid zero amount
            payment_method=PaymentMethod.CREDIT_CARD
        )
        await billing_system.create_transaction(invalid_transaction)

    # Test future date
    with pytest.raises(Exception):
        future_transaction = TransactionCreate(
            patient_id="P12345",
            provider_id="PR67890",
            service_date=date(2026, 1, 1),  # Future date
            amount=Decimal("150.00"),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        await billing_system.create_transaction(future_transaction)

    # Test missing required fields
    with pytest.raises(Exception):
        incomplete_transaction = TransactionCreate(
            patient_id="P12345",
            provider_id="",  # Missing required field
            service_date=date.today(),
            amount=Decimal("150.00"),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        await billing_system.create_transaction(incomplete_transaction)

if __name__ == "__main__":
    pytest.main([__file__])
