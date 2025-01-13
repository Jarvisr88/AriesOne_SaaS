"""Deposit service module."""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.deposit import Deposit, DepositLineItem

class DepositService:
    """Service for handling deposits."""

    def __init__(self, db: Session):
        """Initialize the deposit service."""
        self.db = db

    def create_deposit(
        self, 
        customer_id: int,
        order_id: int,
        amount: float,
        payment_method: str,
        deposit_date: datetime,
        notes: Optional[str] = None,
        line_items: Optional[List[Dict]] = None
    ) -> Deposit:
        """Create a new deposit."""
        # Create deposit
        deposit = Deposit(
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            deposit_date=deposit_date,
            notes=notes
        )
        self.db.add(deposit)
        self.db.flush()  # Get deposit ID

        # Add line items if provided
        if line_items:
            for item in line_items:
                line_item = DepositLineItem(
                    deposit_id=deposit.id,
                    invoice_id=item['invoice_id'],
                    amount=item['amount'],
                    notes=item.get('notes')
                )
                self.db.add(line_item)

        self.db.commit()
        return deposit

    def get_deposit(self, deposit_id: int) -> Optional[Deposit]:
        """Get a deposit by ID."""
        return self.db.query(Deposit).filter(Deposit.id == deposit_id).first()

    def get_deposits_by_customer(self, customer_id: int) -> List[Deposit]:
        """Get all deposits for a customer."""
        return self.db.query(Deposit).filter(
            Deposit.customer_id == customer_id
        ).all()

    def get_deposits_by_order(self, order_id: int) -> List[Deposit]:
        """Get all deposits for an order."""
        return self.db.query(Deposit).filter(
            Deposit.order_id == order_id
        ).all()

    def update_deposit(
        self,
        deposit_id: int,
        amount: Optional[float] = None,
        payment_method: Optional[str] = None,
        deposit_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Optional[Deposit]:
        """Update a deposit."""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return None

        if amount is not None:
            deposit.amount = amount
        if payment_method is not None:
            deposit.payment_method = payment_method
        if deposit_date is not None:
            deposit.deposit_date = deposit_date
        if notes is not None:
            deposit.notes = notes

        self.db.commit()
        return deposit

    def delete_deposit(self, deposit_id: int) -> bool:
        """Delete a deposit."""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return False

        # Delete associated line items first
        self.db.query(DepositLineItem).filter(
            DepositLineItem.deposit_id == deposit_id
        ).delete()

        # Delete deposit
        self.db.delete(deposit)
        self.db.commit()
        return True

    def add_line_item(
        self,
        deposit_id: int,
        invoice_id: int,
        amount: float,
        notes: Optional[str] = None
    ) -> Optional[DepositLineItem]:
        """Add a line item to a deposit."""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return None

        line_item = DepositLineItem(
            deposit_id=deposit_id,
            invoice_id=invoice_id,
            amount=amount,
            notes=notes
        )
        self.db.add(line_item)
        self.db.commit()
        return line_item

    def get_deposit_total(self, deposit_id: int) -> float:
        """Get total amount for a deposit."""
        return self.db.query(DepositLineItem).filter(
            DepositLineItem.deposit_id == deposit_id
        ).with_entities(
            func.sum(DepositLineItem.amount)
        ).scalar() or 0.0
