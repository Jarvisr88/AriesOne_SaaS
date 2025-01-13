"""
Insurance Service Module

This module handles insurance-related operations and policy management.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Dict

class PolicyStatus(Enum):
    """Policy status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TERMED = "termed"

class VerificationStatus(Enum):
    """Verification status values"""
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"
    EXPIRED = "expired"

class CoverageType(Enum):
    """Coverage type values"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    SELF_PAY = "self_pay"

@dataclass
class InsurancePolicy:
    """Insurance policy details"""
    id: int
    patient_id: int
    payer_id: int
    policy_number: str
    group_number: Optional[str]
    coverage_type: str
    effective_date: date
    termination_date: Optional[date]
    verification_status: str
    last_verified_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class PolicyCoverage:
    """Policy coverage details"""
    id: int
    policy_id: int
    product_category_id: int
    coverage_percentage: Decimal
    deductible_amount: Decimal
    deductible_met: Decimal
    max_benefit_amount: Optional[Decimal]
    benefit_used: Decimal
    effective_date: date
    termination_date: Optional[date]
    created_at: datetime
    updated_at: datetime

class InsuranceService:
    """Handles insurance-related operations"""
    
    # Verification thresholds
    VERIFICATION_EXPIRY_DAYS = 30
    
    @classmethod
    def calculate_policy_status(
        cls,
        policy: InsurancePolicy,
        current_date: Optional[date] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Calculate the current status of an insurance policy.
        
        Args:
            policy: Policy to check
            current_date: Date to check against (defaults to today)
            
        Returns:
            Tuple containing:
                - New status value
                - Reason for status (if changed)
        """
        if current_date is None:
            current_date = date.today()
            
        if policy.status == PolicyStatus.CANCELLED.value:
            return policy.status, None
            
        if policy.status == PolicyStatus.TERMED.value:
            return policy.status, None
            
        if policy.termination_date and policy.termination_date < current_date:
            return PolicyStatus.EXPIRED.value, "Policy term expired"
            
        if policy.effective_date > current_date:
            return PolicyStatus.PENDING.value, "Future effective date"
            
        return PolicyStatus.ACTIVE.value, None
        
    @classmethod
    def calculate_verification_status(
        cls,
        policy: InsurancePolicy,
        current_date: Optional[datetime] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Calculate the verification status of a policy.
        
        Args:
            policy: Policy to check
            current_date: Date to check against (defaults to now)
            
        Returns:
            Tuple containing:
                - New verification status
                - Reason for status (if changed)
        """
        if current_date is None:
            current_date = datetime.now()
            
        if not policy.last_verified_date:
            return (
                VerificationStatus.PENDING.value,
                "Never verified"
            )
            
        days_since_verification = (
            current_date - policy.last_verified_date
        ).days
        
        if days_since_verification > cls.VERIFICATION_EXPIRY_DAYS:
            return (
                VerificationStatus.EXPIRED.value,
                f"Last verified {days_since_verification} days ago"
            )
            
        return VerificationStatus.VERIFIED.value, None
        
    @classmethod
    def calculate_coverage(
        cls,
        coverage: PolicyCoverage,
        billed_amount: Decimal,
        current_date: Optional[date] = None
    ) -> Tuple[Decimal, Dict[str, Decimal], List[str]]:
        """
        Calculate coverage for a billed amount.
        
        Args:
            coverage: Coverage details
            billed_amount: Amount to calculate coverage for
            current_date: Date to check against (defaults to today)
            
        Returns:
            Tuple containing:
                - Covered amount
                - Coverage details dictionary
                - List of coverage notes
        """
        if current_date is None:
            current_date = date.today()
            
        notes = []
        details = {
            "billed_amount": billed_amount,
            "covered_amount": Decimal('0'),
            "patient_responsibility": billed_amount,
            "deductible_applied": Decimal('0'),
            "coinsurance_amount": Decimal('0')
        }
        
        # Check coverage dates
        if coverage.termination_date and coverage.termination_date < current_date:
            notes.append("Coverage expired")
            return Decimal('0'), details, notes
            
        if coverage.effective_date > current_date:
            notes.append("Coverage not yet effective")
            return Decimal('0'), details, notes
            
        # Check benefit maximum
        if coverage.max_benefit_amount:
            remaining_benefit = (
                coverage.max_benefit_amount - coverage.benefit_used
            )
            if remaining_benefit <= 0:
                notes.append("Maximum benefit exceeded")
                return Decimal('0'), details, notes
                
            if billed_amount > remaining_benefit:
                notes.append("Partial benefit remaining")
                billed_amount = remaining_benefit
                
        # Apply deductible
        remaining_deductible = (
            coverage.deductible_amount - coverage.deductible_met
        )
        if remaining_deductible > 0:
            deductible_applied = min(remaining_deductible, billed_amount)
            billed_amount -= deductible_applied
            details["deductible_applied"] = deductible_applied
            notes.append(
                f"Applied ${deductible_applied} to deductible"
            )
            
        # Calculate coverage
        if billed_amount > 0:
            covered_amount = (
                billed_amount * (coverage.coverage_percentage / 100)
            ).quantize(Decimal('0.01'))
            coinsurance = (billed_amount - covered_amount).quantize(
                Decimal('0.01')
            )
            
            details.update({
                "covered_amount": covered_amount,
                "coinsurance_amount": coinsurance,
                "patient_responsibility": (
                    details["deductible_applied"] + coinsurance
                )
            })
            
            notes.append(
                f"Coverage at {coverage.coverage_percentage}%: "
                f"${covered_amount}"
            )
            if coinsurance > 0:
                notes.append(f"Coinsurance: ${coinsurance}")
                
        return (
            details["covered_amount"],
            details,
            notes
        )
