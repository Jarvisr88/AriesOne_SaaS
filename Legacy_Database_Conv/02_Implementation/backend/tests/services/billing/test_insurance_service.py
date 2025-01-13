"""
Tests for the insurance service module
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import pytest

from app.services.billing.insurance_service import (
    InsuranceService,
    PolicyStatus,
    VerificationStatus,
    CoverageType,
    InsurancePolicy,
    PolicyCoverage
)

def test_calculate_policy_status():
    """Test policy status calculation"""
    service = InsuranceService()
    now = datetime.now()
    today = date.today()
    
    # Create base policy
    policy = InsurancePolicy(
        id=1,
        patient_id=1000,
        payer_id=100,
        policy_number="POL123",
        group_number="GRP456",
        coverage_type=CoverageType.PRIMARY.value,
        effective_date=today,
        termination_date=None,
        verification_status=VerificationStatus.VERIFIED.value,
        last_verified_date=now,
        status=PolicyStatus.ACTIVE.value,
        created_at=now,
        updated_at=now
    )
    
    # Test cancelled
    policy.status = PolicyStatus.CANCELLED.value
    status, reason = service.calculate_policy_status(policy)
    assert status == PolicyStatus.CANCELLED.value
    assert reason is None
    
    # Test termed
    policy.status = PolicyStatus.TERMED.value
    status, reason = service.calculate_policy_status(policy)
    assert status == PolicyStatus.TERMED.value
    assert reason is None
    
    # Test expired
    policy.status = PolicyStatus.ACTIVE.value
    policy.termination_date = today - timedelta(days=1)
    status, reason = service.calculate_policy_status(policy)
    assert status == PolicyStatus.EXPIRED.value
    assert "expired" in reason.lower()
    
    # Test pending
    policy.termination_date = None
    policy.effective_date = today + timedelta(days=1)
    status, reason = service.calculate_policy_status(policy)
    assert status == PolicyStatus.PENDING.value
    assert "future" in reason.lower()
    
    # Test active
    policy.effective_date = today
    status, reason = service.calculate_policy_status(policy)
    assert status == PolicyStatus.ACTIVE.value
    assert reason is None

def test_calculate_verification_status():
    """Test verification status calculation"""
    service = InsuranceService()
    now = datetime.now()
    today = date.today()
    
    # Create base policy
    policy = InsurancePolicy(
        id=1,
        patient_id=1000,
        payer_id=100,
        policy_number="POL123",
        group_number="GRP456",
        coverage_type=CoverageType.PRIMARY.value,
        effective_date=today,
        termination_date=None,
        verification_status=VerificationStatus.VERIFIED.value,
        last_verified_date=now,
        status=PolicyStatus.ACTIVE.value,
        created_at=now,
        updated_at=now
    )
    
    # Test never verified
    policy.last_verified_date = None
    status, reason = service.calculate_verification_status(policy)
    assert status == VerificationStatus.PENDING.value
    assert "never" in reason.lower()
    
    # Test expired
    policy.last_verified_date = now - timedelta(
        days=service.VERIFICATION_EXPIRY_DAYS + 1
    )
    status, reason = service.calculate_verification_status(policy)
    assert status == VerificationStatus.EXPIRED.value
    assert "days ago" in reason.lower()
    
    # Test verified
    policy.last_verified_date = now
    status, reason = service.calculate_verification_status(policy)
    assert status == VerificationStatus.VERIFIED.value
    assert reason is None

def test_calculate_coverage():
    """Test coverage calculation"""
    service = InsuranceService()
    now = datetime.now()
    today = date.today()
    
    # Create base coverage
    coverage = PolicyCoverage(
        id=1,
        policy_id=1,
        product_category_id=100,
        coverage_percentage=Decimal('80'),
        deductible_amount=Decimal('1000'),
        deductible_met=Decimal('0'),
        max_benefit_amount=Decimal('10000'),
        benefit_used=Decimal('0'),
        effective_date=today,
        termination_date=None,
        created_at=now,
        updated_at=now
    )
    
    # Test expired coverage
    coverage.termination_date = today - timedelta(days=1)
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1000')
    )
    assert covered == Decimal('0')
    assert "expired" in notes[0].lower()
    
    # Test future coverage
    coverage.termination_date = None
    coverage.effective_date = today + timedelta(days=1)
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1000')
    )
    assert covered == Decimal('0')
    assert "not yet effective" in notes[0].lower()
    
    # Test exceeded maximum
    coverage.effective_date = today
    coverage.benefit_used = Decimal('10000')
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1000')
    )
    assert covered == Decimal('0')
    assert "maximum benefit" in notes[0].lower()
    
    # Test partial benefit
    coverage.benefit_used = Decimal('9500')
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1000')
    )
    assert covered == Decimal('400')
    assert "partial benefit" in notes[0].lower()
    
    # Test deductible
    coverage.benefit_used = Decimal('0')
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1200')
    )
    assert covered == Decimal('160')
    assert details["deductible_applied"] == Decimal('1000')
    assert "deductible" in notes[0].lower()
    
    # Test normal coverage
    coverage.deductible_met = Decimal('1000')
    covered, details, notes = service.calculate_coverage(
        coverage=coverage,
        billed_amount=Decimal('1000')
    )
    assert covered == Decimal('800')
    assert details["coinsurance_amount"] == Decimal('200')
    assert "coverage at 80%" in notes[0].lower()
