from typing import Optional, List, Dict
from datetime import datetime
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.financial import (
    Transaction, Account, PurchaseOrder, Claim,
    TransactionAudit
)
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics

class FinancialService:
    def __init__(self, db: Session):
        self.db = db

    async def create_transaction(
        self,
        account_id: uuid.UUID,
        type: str,
        amount: Decimal,
        currency: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        user_id: uuid.UUID = None
    ) -> Transaction:
        """Create new financial transaction"""
        try:
            # Validate account
            account = self.db.query(Account).get(account_id)
            if not account:
                raise ValueError("Account not found")
            if account.status != "ACTIVE":
                raise ValueError("Account is not active")
            
            # Validate amount
            if type in ["WITHDRAWAL", "TRANSFER"] and amount > account.available_balance:
                raise ValueError("Insufficient funds")
            
            # Create transaction
            transaction = Transaction(
                account_id=account_id,
                type=type,
                status="PENDING",
                amount=amount,
                currency=currency,
                description=description,
                metadata=metadata,
                created_by=user_id,
                updated_by=user_id
            )
            
            # Create audit trail
            audit = TransactionAudit(
                transaction=transaction,
                action="CREATE",
                new_status="PENDING",
                user_id=user_id,
                metadata=metadata
            )
            
            self.db.add(transaction)
            self.db.add(audit)
            self.db.commit()
            
            # Update metrics
            metrics.transaction_count.inc()
            metrics.transaction_amount.inc(float(amount))
            
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Transaction creation error: {e}")
            raise

    async def process_transaction(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Transaction:
        """Process pending transaction"""
        try:
            transaction = self.db.query(Transaction).get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Update transaction status
            old_status = transaction.status
            transaction.status = "PROCESSING"
            transaction.updated_by = user_id
            
            # Create audit trail
            audit = TransactionAudit(
                transaction=transaction,
                action="PROCESS",
                old_status=old_status,
                new_status="PROCESSING",
                user_id=user_id
            )
            
            self.db.add(audit)
            
            # Update account balance
            account = transaction.account
            if transaction.type == "DEPOSIT":
                account.balance += transaction.amount
            elif transaction.type in ["WITHDRAWAL", "TRANSFER"]:
                account.balance -= transaction.amount
            
            # Mark as completed
            transaction.status = "COMPLETED"
            
            # Create completion audit
            completion_audit = TransactionAudit(
                transaction=transaction,
                action="COMPLETE",
                old_status="PROCESSING",
                new_status="COMPLETED",
                user_id=user_id
            )
            
            self.db.add(completion_audit)
            self.db.commit()
            
            # Update metrics
            metrics.account_balance.set(float(account.balance))
            
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Transaction processing error: {e}")
            
            # Mark as failed
            if transaction:
                transaction.status = "FAILED"
                failure_audit = TransactionAudit(
                    transaction=transaction,
                    action="FAIL",
                    old_status=old_status,
                    new_status="FAILED",
                    user_id=user_id,
                    metadata={"error": str(e)}
                )
                self.db.add(failure_audit)
                self.db.commit()
            
            raise

    async def create_purchase_order(
        self,
        vendor_id: uuid.UUID,
        items: List[Dict],
        currency: str,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None,
        user_id: uuid.UUID = None
    ) -> PurchaseOrder:
        """Create new purchase order"""
        try:
            # Calculate total amount
            total_amount = sum(
                Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
                for item in items
            )
            
            # Create purchase order
            po = PurchaseOrder(
                vendor_id=vendor_id,
                status="DRAFT",
                total_amount=total_amount,
                currency=currency,
                description=description,
                notes=notes,
                metadata=metadata,
                created_by=user_id,
                updated_by=user_id
            )
            
            # Create items
            for item in items:
                po_item = PurchaseOrderItem(
                    purchase_order=po,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    total_price=Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"])),
                    description=item.get("description")
                )
                self.db.add(po_item)
            
            self.db.add(po)
            self.db.commit()
            
            # Update metrics
            metrics.purchase_order_count.inc()
            
            return po
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Purchase order creation error: {e}")
            raise

    async def submit_claim(
        self,
        patient_id: uuid.UUID,
        provider_id: uuid.UUID,
        amount: Decimal,
        currency: str,
        service_date: datetime,
        diagnosis_codes: List[str],
        procedure_codes: List[str],
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None,
        user_id: uuid.UUID = None
    ) -> Claim:
        """Submit new insurance claim"""
        try:
            # Create claim
            claim = Claim(
                patient_id=patient_id,
                provider_id=provider_id,
                status="SUBMITTED",
                amount=amount,
                currency=currency,
                service_date=service_date,
                diagnosis_codes=diagnosis_codes,
                procedure_codes=procedure_codes,
                notes=notes,
                metadata=metadata,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(claim)
            self.db.commit()
            
            # Update metrics
            metrics.claim_count.inc()
            
            return claim
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Claim submission error: {e}")
            raise

    async def get_account_balance(
        self,
        account_id: uuid.UUID
    ) -> Dict:
        """Get account balance with pending transactions"""
        try:
            account = self.db.query(Account).get(account_id)
            if not account:
                raise ValueError("Account not found")
                
            return {
                "current_balance": float(account.balance),
                "available_balance": float(account.available_balance),
                "currency": account.currency,
                "pending_transactions": [
                    {
                        "id": str(t.id),
                        "type": t.type,
                        "amount": float(t.amount),
                        "status": t.status
                    }
                    for t in account.transactions
                    if t.status == "PENDING"
                ]
            }
            
        except Exception as e:
            logger.error(f"Balance retrieval error: {e}")
            raise

    async def get_transaction_history(
        self,
        account_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get transaction history with filters"""
        try:
            query = self.db.query(Transaction).filter(
                Transaction.account_id == account_id
            )
            
            if start_date:
                query = query.filter(Transaction.created_at >= start_date)
            if end_date:
                query = query.filter(Transaction.created_at <= end_date)
            if transaction_type:
                query = query.filter(Transaction.type == transaction_type)
            if status:
                query = query.filter(Transaction.status == status)
                
            transactions = query.order_by(Transaction.created_at.desc()).all()
            
            return [
                {
                    "id": str(t.id),
                    "type": t.type,
                    "status": t.status,
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "description": t.description,
                    "created_at": t.created_at.isoformat(),
                    "audit_trail": [
                        {
                            "action": a.action,
                            "old_status": a.old_status,
                            "new_status": a.new_status,
                            "timestamp": a.timestamp.isoformat(),
                            "user_id": str(a.user_id)
                        }
                        for a in t.audit_trail
                    ]
                }
                for t in transactions
            ]
            
        except Exception as e:
            logger.error(f"Transaction history error: {e}")
            raise

# Create database session factory
def get_financial_service(db: Session) -> FinancialService:
    return FinancialService(db)
