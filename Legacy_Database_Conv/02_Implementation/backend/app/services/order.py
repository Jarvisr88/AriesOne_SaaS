"""
Order domain business logic and database operations.
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..models.order import Order, OrderDetail, SerialTransaction, OrderSurvey
from ..schemas.order import (
    OrderCreate, OrderUpdate,
    OrderDetailCreate, OrderDetailUpdate,
    SerialTransactionCreate, SerialTransactionUpdate,
    OrderSurveyCreate, OrderSurveyUpdate
)

class OrderService:
    def create_order(self, db: Session, order: OrderCreate) -> Order:
        """Create a new order."""
        db_order = Order(**order.dict())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    def get_order(self, db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID."""
        return db.query(Order).filter(Order.id == order_id).first()

    def list_orders(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        order_type: Optional[str] = None,
        order_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Order]:
        """List orders with optional filters."""
        query = db.query(Order)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        if order_status:
            query = query.filter(Order.order_status == order_status)
        if start_date and end_date:
            query = query.filter(
                and_(
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            )
            
        return query.offset(skip).limit(limit).all()

    def update_order(
        self,
        db: Session,
        order_id: int,
        order: OrderUpdate
    ) -> Optional[Order]:
        """Update order information."""
        db_order = self.get_order(db, order_id)
        if not db_order:
            return None
            
        for key, value in order.dict(exclude_unset=True).items():
            setattr(db_order, key, value)
            
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    def delete_order(self, db: Session, order_id: int) -> bool:
        """Delete order."""
        db_order = self.get_order(db, order_id)
        if not db_order:
            return False
            
        db.delete(db_order)
        db.commit()
        return True

    def add_order_detail(
        self,
        db: Session,
        order_id: int,
        detail: OrderDetailCreate
    ) -> OrderDetail:
        """Add detail to order."""
        db_detail = OrderDetail(
            order_id=order_id,
            **detail.dict()
        )
        db.add(db_detail)
        db.commit()
        db.refresh(db_detail)
        return db_detail

    def list_order_details(
        self,
        db: Session,
        order_id: int
    ) -> List[OrderDetail]:
        """List order details."""
        return (
            db.query(OrderDetail)
            .filter(OrderDetail.order_id == order_id)
            .all()
        )

    def update_order_detail(
        self,
        db: Session,
        detail_id: int,
        detail: OrderDetailUpdate
    ) -> Optional[OrderDetail]:
        """Update order detail."""
        db_detail = (
            db.query(OrderDetail)
            .filter(OrderDetail.id == detail_id)
            .first()
        )
        if not db_detail:
            return None
            
        for key, value in detail.dict(exclude_unset=True).items():
            setattr(db_detail, key, value)
            
        db.add(db_detail)
        db.commit()
        db.refresh(db_detail)
        return db_detail

    def delete_order_detail(self, db: Session, detail_id: int) -> bool:
        """Delete order detail."""
        db_detail = (
            db.query(OrderDetail)
            .filter(OrderDetail.id == detail_id)
            .first()
        )
        if not db_detail:
            return False
            
        db.delete(db_detail)
        db.commit()
        return True

    def create_serial_transaction(
        self,
        db: Session,
        transaction: SerialTransactionCreate
    ) -> SerialTransaction:
        """Create a new serial transaction."""
        db_transaction = SerialTransaction(**transaction.dict())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def get_serial_transaction(
        self,
        db: Session,
        serial_number: str
    ) -> Optional[SerialTransaction]:
        """Get serial transaction by serial number."""
        return (
            db.query(SerialTransaction)
            .filter(SerialTransaction.serial_number == serial_number)
            .first()
        )

    def list_serial_transactions(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_id: Optional[int] = None,
        item_id: Optional[int] = None,
        transaction_type: Optional[str] = None
    ) -> List[SerialTransaction]:
        """List serial transactions with optional filters."""
        query = db.query(SerialTransaction)
        
        if order_id:
            query = query.filter(SerialTransaction.order_id == order_id)
        if item_id:
            query = query.filter(SerialTransaction.item_id == item_id)
        if transaction_type:
            query = query.filter(SerialTransaction.transaction_type == transaction_type)
            
        return query.offset(skip).limit(limit).all()

    def create_order_survey(
        self,
        db: Session,
        order_id: int,
        survey: OrderSurveyCreate
    ) -> OrderSurvey:
        """Create a new order survey."""
        db_survey = OrderSurvey(
            order_id=order_id,
            **survey.dict()
        )
        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
        return db_survey

    def get_order_survey(
        self,
        db: Session,
        order_id: int
    ) -> Optional[OrderSurvey]:
        """Get survey for an order."""
        return (
            db.query(OrderSurvey)
            .filter(OrderSurvey.order_id == order_id)
            .first()
        )

    def update_order_survey(
        self,
        db: Session,
        survey_id: int,
        survey: OrderSurveyUpdate
    ) -> Optional[OrderSurvey]:
        """Update order survey."""
        db_survey = (
            db.query(OrderSurvey)
            .filter(OrderSurvey.id == survey_id)
            .first()
        )
        if not db_survey:
            return None
            
        for key, value in survey.dict(exclude_unset=True).items():
            setattr(db_survey, key, value)
            
        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
        return db_survey
