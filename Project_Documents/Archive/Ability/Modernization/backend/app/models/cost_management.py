from datetime import datetime
from typing import Optional, Dict, List
from decimal import Decimal
from tortoise import fields, models
from pydantic import BaseModel

class CostCenter(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=50)
    parent_id = fields.UUIDField(null=True)
    budget = fields.DecimalField(max_digits=15, decimal_places=2)
    spent = fields.DecimalField(max_digits=15, decimal_places=2)
    currency = fields.CharField(max_length=3)
    status = fields.CharField(max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "cost_centers"

class BudgetAllocation(models.Model):
    id = fields.UUIDField(pk=True)
    cost_center_id = fields.UUIDField()
    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    period_start = fields.DateField()
    period_end = fields.DateField()
    category = fields.CharField(max_length=50)
    status = fields.CharField(max_length=20)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "budget_allocations"
        indexes = (
            ("cost_center_id", "period_start", "period_end"),
        )

class CostTracking(models.Model):
    id = fields.UUIDField(pk=True)
    cost_center_id = fields.UUIDField()
    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    category = fields.CharField(max_length=50)
    description = fields.TextField()
    valuation_method = fields.CharField(max_length=20)
    currency = fields.CharField(max_length=3)
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=6)
    tax_rate = fields.DecimalField(max_digits=5, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "cost_tracking"

class ValuationMethod(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    description = fields.TextField()
    formula = fields.JSONField()
    parameters = fields.JSONField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "valuation_methods"

class ROIAnalysis(models.Model):
    id = fields.UUIDField(pk=True)
    investment_id = fields.UUIDField()
    total_costs = fields.DecimalField(max_digits=15, decimal_places=2)
    total_benefits = fields.DecimalField(max_digits=15, decimal_places=2)
    roi_percentage = fields.DecimalField(max_digits=8, decimal_places=2)
    payback_period = fields.DecimalField(max_digits=8, decimal_places=2)
    npv = fields.DecimalField(max_digits=15, decimal_places=2)
    irr = fields.DecimalField(max_digits=8, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roi_analyses"

class TaxRecord(models.Model):
    id = fields.UUIDField(pk=True)
    transaction_id = fields.UUIDField()
    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = fields.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = fields.DecimalField(max_digits=5, decimal_places=2)
    category = fields.CharField(max_length=50)
    jurisdiction = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tax_records"

class CurrencyExchange(models.Model):
    id = fields.UUIDField(pk=True)
    from_currency = fields.CharField(max_length=3)
    to_currency = fields.CharField(max_length=3)
    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    converted_amount = fields.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=6)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "currency_exchanges"

class MarginAnalysis(models.Model):
    id = fields.UUIDField(pk=True)
    product_id = fields.UUIDField()
    total_costs = fields.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = fields.DecimalField(max_digits=15, decimal_places=2)
    gross_margin = fields.DecimalField(max_digits=8, decimal_places=2)
    operating_margin = fields.DecimalField(max_digits=8, decimal_places=2)
    net_margin = fields.DecimalField(max_digits=8, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "margin_analyses"

# Pydantic models for API
class CostCenterCreate(BaseModel):
    name: str
    code: str
    parent_id: Optional[str]
    budget: Decimal
    currency: str

class BudgetAllocationCreate(BaseModel):
    cost_center_id: str
    amount: Decimal
    period_start: datetime
    period_end: datetime
    category: str
    notes: Optional[str]

class CostTrackingCreate(BaseModel):
    cost_center_id: str
    amount: Decimal
    category: str
    description: str
    valuation_method: str
    currency: str

class ROIAnalysisCreate(BaseModel):
    investment_id: str
    cost_items: List[Dict]
    benefit_items: List[Dict]
    timeframe: int

class TaxRecordCreate(BaseModel):
    transaction_id: str
    amount: Decimal
    category: str
    jurisdiction: str

class CurrencyExchangeCreate(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal

class MarginAnalysisCreate(BaseModel):
    product_id: str
    revenue_data: Dict
    cost_data: Dict
