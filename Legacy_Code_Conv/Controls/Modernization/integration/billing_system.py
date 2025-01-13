from typing import Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, condecimal
import httpx
import logging
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    VOIDED = "voided"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    ACH = "ach"
    CHECK = "check"
    CASH = "cash"
    INSURANCE = "insurance"

class BillingTransaction(Base):
    __tablename__ = 'billing_transactions'

    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True)
    patient_id = Column(String, ForeignKey('patients.id'))
    provider_id = Column(String, ForeignKey('providers.id'))
    service_date = Column(Date)
    amount = Column(Numeric(10, 2))
    payment_method = Column(String)
    status = Column(String)
    insurance_claim_id = Column(String, nullable=True)
    reference_number = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TransactionCreate(BaseModel):
    patient_id: str
    provider_id: str
    service_date: date
    amount: condecimal(max_digits=10, decimal_places=2)
    payment_method: PaymentMethod
    insurance_claim_id: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class BillingSystemIntegration:
    def __init__(self, db_url: str, api_base_url: str, api_key: str):
        # Database setup
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # API configuration
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def create_transaction(
        self,
        transaction: TransactionCreate
    ) -> Dict:
        """Create a new billing transaction"""
        session = self.Session()
        try:
            # Create transaction in external system first
            external_transaction = await self._create_external_transaction(transaction)

            # Create local transaction record
            db_transaction = BillingTransaction(
                external_id=external_transaction["id"],
                patient_id=transaction.patient_id,
                provider_id=transaction.provider_id,
                service_date=transaction.service_date,
                amount=transaction.amount,
                payment_method=transaction.payment_method,
                status=PaymentStatus.PENDING,
                insurance_claim_id=transaction.insurance_claim_id,
                reference_number=transaction.reference_number,
                notes=transaction.notes
            )

            session.add(db_transaction)
            session.commit()

            # Track the transaction creation
            from services.analytics_service import analytics_service
            await analytics_service.track_action(
                action=UserAction(
                    timestamp=datetime.utcnow(),
                    user_id=transaction.provider_id,
                    component="billing",
                    action="create_transaction",
                    data={
                        "transaction_id": db_transaction.id,
                        "amount": float(transaction.amount),
                        "payment_method": transaction.payment_method
                    }
                )
            )

            return {
                "status": "success",
                "transaction_id": db_transaction.id,
                "external_id": db_transaction.external_id
            }

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create transaction: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create transaction: {str(e)}"
            )
        finally:
            session.close()

    async def process_payment(
        self,
        transaction_id: int,
        payment_details: Dict
    ) -> Dict:
        """Process payment for a transaction"""
        session = self.Session()
        try:
            transaction = session.query(BillingTransaction).get(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=404,
                    detail="Transaction not found"
                )

            # Process payment in external system
            payment_result = await self._process_external_payment(
                transaction.external_id,
                payment_details
            )

            # Update local transaction status
            transaction.status = payment_result["status"]
            transaction.updated_at = datetime.utcnow()
            session.commit()

            return {
                "status": "success",
                "payment_status": transaction.status,
                "transaction_id": transaction.id
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to process payment: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process payment: {str(e)}"
            )
        finally:
            session.close()

    async def _create_external_transaction(
        self,
        transaction: TransactionCreate
    ) -> Dict:
        """Create transaction in external billing system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/transactions",
                    headers=self.headers,
                    json={
                        "patient_id": transaction.patient_id,
                        "provider_id": transaction.provider_id,
                        "service_date": transaction.service_date.isoformat(),
                        "amount": str(transaction.amount),
                        "payment_method": transaction.payment_method,
                        "insurance_claim_id": transaction.insurance_claim_id,
                        "reference_number": transaction.reference_number,
                        "notes": transaction.notes
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to create external transaction: {e}")
            raise

    async def _process_external_payment(
        self,
        external_id: str,
        payment_details: Dict
    ) -> Dict:
        """Process payment in external billing system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/transactions/{external_id}/payments",
                    headers=self.headers,
                    json=payment_details
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to process external payment: {e}")
            raise

    async def get_transaction_history(
        self,
        patient_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Dict]:
        """Get transaction history with optional filters"""
        session = self.Session()
        try:
            query = session.query(BillingTransaction)

            if patient_id:
                query = query.filter(BillingTransaction.patient_id == patient_id)
            if provider_id:
                query = query.filter(BillingTransaction.provider_id == provider_id)
            if start_date:
                query = query.filter(BillingTransaction.service_date >= start_date)
            if end_date:
                query = query.filter(BillingTransaction.service_date <= end_date)
            if status:
                query = query.filter(BillingTransaction.status == status)

            transactions = query.order_by(BillingTransaction.service_date.desc()).all()

            return [{
                "id": t.id,
                "external_id": t.external_id,
                "patient_id": t.patient_id,
                "provider_id": t.provider_id,
                "service_date": t.service_date.isoformat(),
                "amount": str(t.amount),
                "payment_method": t.payment_method,
                "status": t.status,
                "insurance_claim_id": t.insurance_claim_id,
                "reference_number": t.reference_number,
                "notes": t.notes,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            } for t in transactions]

        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get transaction history: {str(e)}"
            )
        finally:
            session.close()

    async def void_transaction(self, transaction_id: int) -> Dict:
        """Void a transaction"""
        session = self.Session()
        try:
            transaction = session.query(BillingTransaction).get(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=404,
                    detail="Transaction not found"
                )

            if transaction.status not in [PaymentStatus.PENDING, PaymentStatus.AUTHORIZED]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot void transaction with status {transaction.status}"
                )

            # Void transaction in external system
            await self._void_external_transaction(transaction.external_id)

            # Update local transaction status
            transaction.status = PaymentStatus.VOIDED
            transaction.updated_at = datetime.utcnow()
            session.commit()

            return {
                "status": "success",
                "message": "Transaction voided successfully",
                "transaction_id": transaction.id
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to void transaction: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to void transaction: {str(e)}"
            )
        finally:
            session.close()

    async def _void_external_transaction(self, external_id: str):
        """Void transaction in external billing system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/transactions/{external_id}/void",
                    headers=self.headers
                )
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to void external transaction: {e}")
            raise

# Initialize global integration service
billing_system = BillingSystemIntegration(
    db_url="postgresql://user:password@localhost/billing_db",
    api_base_url="https://api.billing.com/v1",
    api_key="your-api-key"
)
