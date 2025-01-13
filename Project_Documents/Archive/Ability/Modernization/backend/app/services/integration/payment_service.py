from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    PaymentGateway,
    PaymentTransaction,
    PaymentMethod
)

class PaymentService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.gateways = self._load_gateways()

    async def process_payment(
        self,
        amount: float,
        currency: str,
        payment_method: Dict,
        order_id: str
    ) -> Dict:
        """Process payment through appropriate gateway"""
        try:
            # Select payment gateway
            gateway = await self._select_gateway(payment_method["type"])
            
            # Prepare payment data
            payment_data = await self._prepare_payment_data(
                amount,
                currency,
                payment_method,
                order_id
            )
            
            # Process through gateway
            response = await gateway.process_payment(payment_data)
            
            # Log transaction
            transaction = await self._log_transaction(
                gateway.id,
                payment_data,
                response
            )
            
            return {
                "status": "success",
                "transaction_id": transaction.id,
                "gateway_response": response,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict:
        """Process refund for a payment"""
        try:
            # Get original transaction
            transaction = await PaymentTransaction.get(id=transaction_id)
            
            # Select gateway
            gateway = await self._select_gateway_by_id(
                transaction.gateway_id
            )
            
            # Prepare refund data
            refund_data = await self._prepare_refund_data(
                transaction,
                amount
            )
            
            # Process refund through gateway
            response = await gateway.process_refund(refund_data)
            
            # Log refund transaction
            refund = await self._log_transaction(
                gateway.id,
                refund_data,
                response,
                transaction_type="refund"
            )
            
            return {
                "status": "success",
                "refund_id": refund.id,
                "gateway_response": response,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_payment(
        self,
        transaction_id: str
    ) -> Dict:
        """Verify payment status with gateway"""
        try:
            # Get transaction
            transaction = await PaymentTransaction.get(id=transaction_id)
            
            # Select gateway
            gateway = await self._select_gateway_by_id(
                transaction.gateway_id
            )
            
            # Verify with gateway
            status = await gateway.verify_payment(
                transaction.gateway_transaction_id
            )
            
            # Update transaction status
            await self._update_transaction_status(
                transaction_id,
                status
            )
            
            return {
                "status": "success",
                "payment_status": status,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _select_gateway(self, payment_type: str) -> PaymentGateway:
        """Select appropriate payment gateway"""
        gateway = self.gateways.get(payment_type)
        if not gateway:
            raise ValueError(f"No gateway found for {payment_type}")
        return gateway

    async def _select_gateway_by_id(
        self,
        gateway_id: str
    ) -> PaymentGateway:
        """Select gateway by ID"""
        for gateway in self.gateways.values():
            if gateway.id == gateway_id:
                return gateway
        raise ValueError(f"No gateway found with ID {gateway_id}")

    async def _prepare_payment_data(
        self,
        amount: float,
        currency: str,
        payment_method: Dict,
        order_id: str
    ) -> Dict:
        """Prepare payment data for gateway"""
        return {
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "order_id": order_id,
            "timestamp": datetime.now().isoformat()
        }

    async def _prepare_refund_data(
        self,
        transaction: PaymentTransaction,
        amount: Optional[float]
    ) -> Dict:
        """Prepare refund data for gateway"""
        return {
            "original_transaction_id": transaction.gateway_transaction_id,
            "amount": amount or transaction.amount,
            "currency": transaction.currency,
            "reason": "Customer requested refund",
            "timestamp": datetime.now().isoformat()
        }

    async def _log_transaction(
        self,
        gateway_id: str,
        request_data: Dict,
        response_data: Dict,
        transaction_type: str = "payment"
    ) -> PaymentTransaction:
        """Log payment transaction"""
        return await PaymentTransaction.create(
            gateway_id=gateway_id,
            transaction_type=transaction_type,
            amount=request_data["amount"],
            currency=request_data["currency"],
            status=response_data["status"],
            gateway_transaction_id=response_data["transaction_id"],
            request_data=request_data,
            response_data=response_data,
            created_at=datetime.now()
        )

    async def _update_transaction_status(
        self,
        transaction_id: str,
        status: str
    ) -> None:
        """Update transaction status"""
        transaction = await PaymentTransaction.get(id=transaction_id)
        transaction.status = status
        transaction.updated_at = datetime.now()
        await transaction.save()
