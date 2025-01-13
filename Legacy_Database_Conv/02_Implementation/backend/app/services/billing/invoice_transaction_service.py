"""
Invoice transaction service for handling invoice adjustments and transactions
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Tuple

class TransactionType(str, Enum):
    """Transaction types for invoice adjustments"""
    ADJUST_ALLOWABLE = "Adjust Allowable"
    ADJUST_CUSTOMARY = "Adjust Customary" 
    ADJUST_TAXES = "Adjust Taxes"

@dataclass
class InvoiceTransaction:
    """Invoice transaction data"""
    id: int
    customer_id: int
    invoice_id: int
    invoice_details_id: int
    transaction_type_id: int
    transaction_type: TransactionType
    amount: Decimal
    quantity: float
    comments: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class InvoiceDetail:
    """Invoice detail data"""
    id: int
    customer_id: int
    invoice_id: int
    allowable_amount: Decimal
    billable_amount: Decimal
    taxes: Decimal
    quantity: float

class InvoiceTransactionService:
    """Service for handling invoice transactions and adjustments"""
    
    AMOUNT_THRESHOLD = Decimal('0.001')
    
    def process_transaction(
        self,
        transaction: InvoiceTransaction,
        invoice_detail: InvoiceDetail
    ) -> Tuple[InvoiceTransaction, InvoiceDetail]:
        """
        Process an invoice transaction and update the related invoice detail
        
        Args:
            transaction: Transaction to process
            invoice_detail: Related invoice detail
            
        Returns:
            Tuple of (updated transaction, updated invoice detail)
        """
        # Set quantity from invoice detail
        transaction.quantity = invoice_detail.quantity
        
        if transaction.transaction_type == TransactionType.ADJUST_ALLOWABLE:
            # Handle allowable amount adjustment
            old_value = invoice_detail.allowable_amount
            transaction.comments = f"Previous Value={old_value}"
            
            if abs(old_value - transaction.amount) > self.AMOUNT_THRESHOLD:
                invoice_detail.allowable_amount = transaction.amount
                
        elif transaction.transaction_type == TransactionType.ADJUST_CUSTOMARY:
            # Handle billable amount adjustment
            old_value = invoice_detail.billable_amount
            transaction.comments = f"Previous Value={old_value}"
            
            if abs(old_value - transaction.amount) > self.AMOUNT_THRESHOLD:
                invoice_detail.billable_amount = transaction.amount
                
        elif transaction.transaction_type == TransactionType.ADJUST_TAXES:
            # Handle tax adjustment
            old_value = invoice_detail.taxes
            transaction.comments = f"Previous Value={old_value}"
            
            if abs(old_value - transaction.amount) > self.AMOUNT_THRESHOLD:
                invoice_detail.taxes = transaction.amount
                
        return transaction, invoice_detail
