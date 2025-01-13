"""
Price calculation module using modern calculation engine.
"""
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, validator
from fastapi import HTTPException
from ...repositories.price_repository import PriceRepository
from ...repositories.models import PriceList, PriceListItem
from ...core.database import Database

class DiscountRule(BaseModel):
    """Discount rule model."""
    type: str  # percentage, fixed, or quantity_break
    value: Decimal
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_type: Optional[str] = None

    @validator('type')
    def valid_type(cls, v):
        """Validate discount type."""
        valid_types = ['percentage', 'fixed', 'quantity_break']
        if v not in valid_types:
            raise ValueError(f'Invalid discount type. Must be one of: {", ".join(valid_types)}')
        return v

    @validator('value')
    def valid_value(cls, v, values):
        """Validate discount value."""
        if values.get('type') == 'percentage' and (v <= 0 or v > 100):
            raise ValueError('Percentage discount must be between 0 and 100')
        elif values.get('type') in ['fixed', 'quantity_break'] and v <= 0:
            raise ValueError('Fixed discount must be greater than 0')
        return v

class PriceCalculation(BaseModel):
    """Price calculation result."""
    original_price: Decimal
    quantity: int
    subtotal: Decimal
    discounts: List[Dict[str, Decimal]]
    total_discount: Decimal
    final_price: Decimal
    unit_price: Decimal
    effective_discount_percentage: Decimal

class PriceCalculator:
    """Handle price calculations with discounts and quantity breaks."""
    
    def __init__(self, database: Database):
        self.database = database
        self.price_repository = PriceRepository(database)

    async def get_base_price(
        self,
        price_list_id: int,
        item_code: str,
        quantity: int
    ) -> PriceListItem:
        """Get base price for item."""
        # Get price list item
        item = await self.price_repository.get_item_by_code(
            price_list_id,
            item_code
        )
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Price list item not found"
            )

        # Validate quantity
        if quantity < item.minimum_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum quantity is {item.minimum_quantity}"
            )
        if item.maximum_quantity and quantity > item.maximum_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum quantity is {item.maximum_quantity}"
            )

        return item

    async def apply_quantity_breaks(
        self,
        item: PriceListItem,
        quantity: int
    ) -> Decimal:
        """Apply quantity break discounts."""
        # Get quantity breaks for item
        quantity_breaks = await self.price_repository.get_quantity_breaks(item.id)
        
        # Sort by minimum quantity descending
        quantity_breaks.sort(key=lambda x: x.min_quantity, reverse=True)
        
        # Find applicable quantity break
        for break_ in quantity_breaks:
            if quantity >= break_.min_quantity:
                if not break_.max_quantity or quantity <= break_.max_quantity:
                    return break_.discount_amount
                
        return Decimal('0')

    async def apply_customer_discounts(
        self,
        price_list_id: int,
        customer_type: str
    ) -> List[DiscountRule]:
        """Get customer-specific discounts."""
        # Get customer discounts
        discounts = await self.price_repository.get_customer_discounts(
            price_list_id,
            customer_type
        )
        
        # Filter active discounts
        now = datetime.utcnow()
        active_discounts = [
            DiscountRule(**discount.dict())
            for discount in discounts
            if (not discount.start_date or discount.start_date <= now) and
               (not discount.end_date or discount.end_date >= now)
        ]
        
        return active_discounts

    def calculate_discount_amount(
        self,
        base_price: Decimal,
        quantity: int,
        discount: DiscountRule
    ) -> Decimal:
        """Calculate discount amount."""
        if discount.type == 'percentage':
            return (base_price * quantity * discount.value) / 100
        elif discount.type == 'fixed':
            return discount.value * quantity
        elif discount.type == 'quantity_break':
            if (not discount.min_quantity or quantity >= discount.min_quantity) and \
               (not discount.max_quantity or quantity <= discount.max_quantity):
                return discount.value * quantity
        return Decimal('0')

    async def calculate_price(
        self,
        price_list_id: int,
        item_code: str,
        quantity: int,
        customer_type: Optional[str] = None
    ) -> PriceCalculation:
        """Calculate final price with all applicable discounts."""
        # Get base price
        item = await self.get_base_price(price_list_id, item_code, quantity)
        base_price = item.unit_price
        subtotal = base_price * quantity

        # Initialize discount tracking
        discounts = []
        total_discount = Decimal('0')

        # Apply quantity breaks
        quantity_discount = await self.apply_quantity_breaks(item, quantity)
        if quantity_discount > 0:
            discounts.append({
                'type': 'quantity_break',
                'amount': quantity_discount
            })
            total_discount += quantity_discount

        # Apply customer discounts
        if customer_type:
            customer_discounts = await self.apply_customer_discounts(
                price_list_id,
                customer_type
            )
            for discount in customer_discounts:
                amount = self.calculate_discount_amount(
                    base_price,
                    quantity,
                    discount
                )
                if amount > 0:
                    discounts.append({
                        'type': discount.type,
                        'amount': amount
                    })
                    total_discount += amount

        # Calculate final prices
        final_total = subtotal - total_discount
        final_unit_price = final_total / quantity
        
        # Calculate effective discount percentage
        effective_discount_percentage = (
            (Decimal('100') * total_discount / subtotal)
            if subtotal > 0 else Decimal('0')
        )

        # Create price calculation result
        return PriceCalculation(
            original_price=base_price,
            quantity=quantity,
            subtotal=subtotal,
            discounts=discounts,
            total_discount=total_discount,
            final_price=final_total,
            unit_price=final_unit_price,
            effective_discount_percentage=effective_discount_percentage
        )

    async def save_price_history(
        self,
        price_list_id: int,
        item_code: str,
        calculation: PriceCalculation,
        customer_type: Optional[str],
        user: str
    ):
        """Save price calculation history."""
        await self.price_repository.create_price_history(
            price_list_id=price_list_id,
            item_code=item_code,
            original_price=calculation.original_price,
            quantity=calculation.quantity,
            discounts=calculation.discounts,
            final_price=calculation.final_price,
            customer_type=customer_type,
            created_by=user
        )
