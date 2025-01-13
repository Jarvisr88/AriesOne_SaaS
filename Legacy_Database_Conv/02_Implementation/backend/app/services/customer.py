"""
Customer domain business logic and database operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.customer import Customer, CustomerInsurance, CustomerNote
from ..schemas.customer import (
    CustomerCreate, CustomerUpdate,
    CustomerInsuranceCreate, CustomerNoteCreate
)

class CustomerService:
    def create_customer(self, db: Session, customer: CustomerCreate) -> Customer:
        """Create a new customer."""
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    def get_customer(self, db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return db.query(Customer).filter(Customer.id == customer_id).first()

    def list_customers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Customer]:
        """List customers with optional search and pagination."""
        query = db.query(Customer)
        
        if search:
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.account_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()

    def update_customer(
        self,
        db: Session,
        customer_id: int,
        customer: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer information."""
        db_customer = self.get_customer(db, customer_id)
        if not db_customer:
            return None
            
        for key, value in customer.dict(exclude_unset=True).items():
            setattr(db_customer, key, value)
            
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    def delete_customer(self, db: Session, customer_id: int) -> bool:
        """Delete customer."""
        db_customer = self.get_customer(db, customer_id)
        if not db_customer:
            return False
            
        db.delete(db_customer)
        db.commit()
        return True

    def add_insurance(
        self,
        db: Session,
        customer_id: int,
        insurance: CustomerInsuranceCreate
    ) -> CustomerInsurance:
        """Add insurance policy to customer."""
        db_insurance = CustomerInsurance(
            customer_id=customer_id,
            **insurance.dict()
        )
        db.add(db_insurance)
        db.commit()
        db.refresh(db_insurance)
        return db_insurance

    def list_insurance(
        self,
        db: Session,
        customer_id: int
    ) -> List[CustomerInsurance]:
        """List customer's insurance policies."""
        return (
            db.query(CustomerInsurance)
            .filter(CustomerInsurance.customer_id == customer_id)
            .all()
        )

    def add_note(
        self,
        db: Session,
        customer_id: int,
        note: CustomerNoteCreate
    ) -> CustomerNote:
        """Add note to customer."""
        db_note = CustomerNote(
            customer_id=customer_id,
            **note.dict()
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    def list_notes(
        self,
        db: Session,
        customer_id: int
    ) -> List[CustomerNote]:
        """List customer's notes."""
        return (
            db.query(CustomerNote)
            .filter(CustomerNote.customer_id == customer_id)
            .order_by(CustomerNote.note_date.desc())
            .all()
        )
