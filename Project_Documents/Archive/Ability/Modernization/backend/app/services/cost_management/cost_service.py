from datetime import datetime, date
from typing import List, Dict, Optional
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.financial import (
    CostCenter,
    BudgetAllocation,
    CostTracking,
    ValuationMethod,
    ROIAnalysis,
    TaxRecord,
    CurrencyExchange,
    MarginAnalysis
)

class CostManagementService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.tax_rates = self._load_tax_rates()
        self.exchange_rates = self._load_exchange_rates()

    async def track_costs(
        self,
        cost_center_id: UUID,
        cost_data: Dict
    ) -> CostTracking:
        """
        Track costs for a specific cost center
        """
        try:
            # Validate cost data
            self._validate_cost_data(cost_data)

            # Apply valuation method
            valued_cost = await self._apply_valuation_method(
                cost_data['amount'],
                cost_data['valuation_method']
            )

            # Create cost tracking record
            tracking = await CostTracking.create(
                cost_center_id=cost_center_id,
                amount=valued_cost,
                category=cost_data['category'],
                description=cost_data['description'],
                valuation_method=cost_data['valuation_method'],
                currency=cost_data['currency'],
                exchange_rate=await self._get_exchange_rate(
                    cost_data['currency']
                ),
                tax_rate=await self._get_tax_rate(
                    cost_data['category']
                ),
                created_at=datetime.now()
            )

            # Update budget allocation
            await self._update_budget_allocation(
                cost_center_id,
                valued_cost
            )

            return tracking

        except Exception as e:
            logger.error(f"Error tracking costs: {str(e)}")
            raise

    async def analyze_roi(
        self,
        investment_data: Dict
    ) -> ROIAnalysis:
        """
        Analyze return on investment
        """
        try:
            # Calculate costs
            total_costs = await self._calculate_total_costs(
                investment_data['cost_items']
            )

            # Calculate benefits
            total_benefits = await self._calculate_total_benefits(
                investment_data['benefit_items']
            )

            # Calculate ROI metrics
            roi_metrics = self._calculate_roi_metrics(
                total_costs,
                total_benefits,
                investment_data['timeframe']
            )

            return await ROIAnalysis.create(
                investment_id=investment_data['id'],
                total_costs=total_costs,
                total_benefits=total_benefits,
                roi_percentage=roi_metrics['roi_percentage'],
                payback_period=roi_metrics['payback_period'],
                npv=roi_metrics['npv'],
                irr=roi_metrics['irr'],
                created_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing ROI: {str(e)}")
            raise

    async def allocate_costs(
        self,
        allocation_data: Dict
    ) -> List[CostCenter]:
        """
        Allocate costs across cost centers
        """
        try:
            # Validate allocation data
            self._validate_allocation_data(allocation_data)

            # Calculate allocations
            allocations = self._calculate_allocations(
                allocation_data['total_amount'],
                allocation_data['allocation_method'],
                allocation_data['cost_centers']
            )

            # Update cost centers
            updated_centers = []
            for allocation in allocations:
                center = await self._update_cost_center(
                    allocation['center_id'],
                    allocation['amount']
                )
                updated_centers.append(center)

            return updated_centers

        except Exception as e:
            logger.error(f"Error allocating costs: {str(e)}")
            raise

    async def analyze_margins(
        self,
        product_data: Dict
    ) -> MarginAnalysis:
        """
        Analyze product margins
        """
        try:
            # Calculate costs
            total_costs = await self._calculate_product_costs(
                product_data['id']
            )

            # Calculate revenue
            total_revenue = await self._calculate_product_revenue(
                product_data['id']
            )

            # Calculate margins
            margins = self._calculate_margins(
                total_costs,
                total_revenue
            )

            return await MarginAnalysis.create(
                product_id=product_data['id'],
                total_costs=total_costs,
                total_revenue=total_revenue,
                gross_margin=margins['gross'],
                net_margin=margins['net'],
                operating_margin=margins['operating'],
                created_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing margins: {str(e)}")
            raise

    async def handle_tax_compliance(
        self,
        transaction_data: Dict
    ) -> TaxRecord:
        """
        Handle tax compliance for transactions
        """
        try:
            # Calculate tax
            tax_amount = await self._calculate_tax(
                transaction_data['amount'],
                transaction_data['category']
            )

            # Create tax record
            tax_record = await TaxRecord.create(
                transaction_id=transaction_data['id'],
                amount=transaction_data['amount'],
                tax_amount=tax_amount,
                tax_rate=await self._get_tax_rate(
                    transaction_data['category']
                ),
                category=transaction_data['category'],
                jurisdiction=transaction_data['jurisdiction'],
                created_at=datetime.now()
            )

            # Update tax tracking
            await self._update_tax_tracking(tax_record)

            return tax_record

        except Exception as e:
            logger.error(f"Error handling tax compliance: {str(e)}")
            raise

    async def handle_currency_conversion(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """
        Handle currency conversion
        """
        try:
            # Get exchange rates
            exchange_rate = await self._get_exchange_rate(
                from_currency,
                to_currency
            )

            # Convert amount
            converted_amount = amount * exchange_rate

            # Create exchange record
            exchange = await CurrencyExchange.create(
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                converted_amount=converted_amount,
                exchange_rate=exchange_rate,
                created_at=datetime.now()
            )

            return {
                'original_amount': amount,
                'converted_amount': converted_amount,
                'exchange_rate': exchange_rate,
                'exchange_id': exchange.id
            }

        except Exception as e:
            logger.error(f"Error converting currency: {str(e)}")
            raise

    def _validate_cost_data(self, cost_data: Dict) -> None:
        """
        Validate cost tracking data
        """
        required_fields = [
            'amount',
            'category',
            'description',
            'valuation_method',
            'currency'
        ]
        for field in required_fields:
            if field not in cost_data:
                raise ValueError(f"Missing required field: {field}")

    async def _apply_valuation_method(
        self,
        amount: Decimal,
        method: str
    ) -> Decimal:
        """
        Apply valuation method to cost
        """
        if method == 'FIFO':
            return await self._apply_fifo(amount)
        elif method == 'LIFO':
            return await self._apply_lifo(amount)
        elif method == 'average':
            return await self._apply_average_cost(amount)
        else:
            return amount

    async def _calculate_roi_metrics(
        self,
        costs: Decimal,
        benefits: Decimal,
        timeframe: int
    ) -> Dict:
        """
        Calculate ROI metrics
        """
        roi_percentage = ((benefits - costs) / costs) * 100
        payback_period = costs / (benefits / timeframe)
        npv = self._calculate_npv(costs, benefits, timeframe)
        irr = self._calculate_irr(costs, benefits, timeframe)

        return {
            'roi_percentage': roi_percentage,
            'payback_period': payback_period,
            'npv': npv,
            'irr': irr
        }

    def _calculate_margins(
        self,
        costs: Decimal,
        revenue: Decimal
    ) -> Dict:
        """
        Calculate various margin metrics
        """
        gross_margin = ((revenue - costs) / revenue) * 100
        operating_costs = costs * Decimal('0.7')  # Example calculation
        operating_margin = (
            (revenue - costs - operating_costs) / revenue
        ) * 100
        net_margin = (
            (revenue - costs - operating_costs) / revenue
        ) * 100 * Decimal('0.8')  # After tax

        return {
            'gross': gross_margin,
            'operating': operating_margin,
            'net': net_margin
        }

    async def _get_tax_rate(
        self,
        category: str,
        jurisdiction: Optional[str] = None
    ) -> Decimal:
        """
        Get applicable tax rate
        """
        return self.tax_rates.get(
            (category, jurisdiction),
            self.tax_rates.get(category, Decimal('0.0'))
        )

    async def _get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str = 'USD'
    ) -> Decimal:
        """
        Get current exchange rate
        """
        key = f"{from_currency}_{to_currency}"
        return self.exchange_rates.get(
            key,
            Decimal('1.0')
        )
