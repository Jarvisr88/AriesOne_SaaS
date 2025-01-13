from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.models.financial import Account, Transaction, PurchaseOrder, Claim
from app.services.financial import FinancialService

class BusinessState:
    """Business process state tracking"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ValidationRule:
    """Base validation rule"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def validate(self, data: Dict) -> tuple[bool, Optional[str]]:
        """Validate data against rule"""
        raise NotImplementedError

class RequiredFieldRule(ValidationRule):
    """Required field validation"""
    def __init__(self, field: str):
        super().__init__(
            f"required_{field}",
            f"Field {field} is required"
        )
        self.field = field

    async def validate(self, data: Dict) -> tuple[bool, Optional[str]]:
        if self.field not in data or not data[self.field]:
            return False, f"Field {self.field} is required"
        return True, None

class RangeRule(ValidationRule):
    """Numeric range validation"""
    def __init__(self, field: str, min_value: float, max_value: float):
        super().__init__(
            f"range_{field}",
            f"Field {field} must be between {min_value} and {max_value}"
        )
        self.field = field
        self.min_value = min_value
        self.max_value = max_value

    async def validate(self, data: Dict) -> tuple[bool, Optional[str]]:
        value = data.get(self.field)
        if value is None:
            return True, None
        if not isinstance(value, (int, float)):
            return False, f"Field {self.field} must be numeric"
        if value < self.min_value or value > self.max_value:
            return False, f"Field {self.field} must be between {self.min_value} and {self.max_value}"
        return True, None

class BusinessProcess:
    """Base business process"""
    def __init__(
        self,
        db: Session,
        process_id: uuid.UUID,
        user_id: uuid.UUID
    ):
        self.db = db
        self.process_id = process_id
        self.user_id = user_id
        self.state = BusinessState.DRAFT
        self.validation_rules: List[ValidationRule] = []
        self.errors: List[str] = []
        self.metrics = self._setup_metrics()
        self._setup_validation_rules()

    def _setup_metrics(self) -> Dict:
        """Setup process metrics"""
        return {
            "processing_time": metrics.business_processing_time,
            "validation_time": metrics.business_validation_time,
            "error_count": metrics.business_error_count,
            "success_rate": metrics.business_success_rate
        }

    def _setup_validation_rules(self):
        """Setup validation rules"""
        raise NotImplementedError

    async def validate(self, data: Dict) -> bool:
        """Validate process data"""
        start_time = datetime.utcnow()
        self.state = BusinessState.VALIDATING
        self.errors = []
        
        try:
            for rule in self.validation_rules:
                valid, error = await rule.validate(data)
                if not valid:
                    self.errors.append(error)
            
            validation_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["validation_time"].observe(validation_time)
            
            return len(self.errors) == 0
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            self.errors.append(str(e))
            self.metrics["error_count"].inc()
            return False

    async def process(self, data: Dict) -> Dict:
        """Process business logic"""
        raise NotImplementedError

    async def get_state(self) -> Dict:
        """Get process state"""
        return {
            "process_id": str(self.process_id),
            "state": self.state,
            "errors": self.errors
        }

class ClaimSubmissionProcess(BusinessProcess):
    """Claim submission business process"""
    def _setup_validation_rules(self):
        """Setup claim validation rules"""
        self.validation_rules = [
            RequiredFieldRule("patient_id"),
            RequiredFieldRule("provider_id"),
            RequiredFieldRule("amount"),
            RequiredFieldRule("service_date"),
            RequiredFieldRule("diagnosis_codes"),
            RequiredFieldRule("procedure_codes"),
            RangeRule("amount", 0.01, 1000000.00)
        ]

    async def process(self, data: Dict) -> Dict:
        """Process claim submission"""
        start_time = datetime.utcnow()
        self.state = BusinessState.PROCESSING
        
        try:
            # Validate data
            if not await self.validate(data):
                self.state = BusinessState.FAILED
                return await self.get_state()
            
            # Create financial service
            financial_service = FinancialService(self.db)
            
            # Submit claim
            claim = await financial_service.submit_claim(
                patient_id=uuid.UUID(data["patient_id"]),
                provider_id=uuid.UUID(data["provider_id"]),
                amount=data["amount"],
                currency=data.get("currency", "USD"),
                service_date=datetime.fromisoformat(data["service_date"]),
                diagnosis_codes=data["diagnosis_codes"],
                procedure_codes=data["procedure_codes"],
                notes=data.get("notes"),
                metadata=data.get("metadata"),
                user_id=self.user_id
            )
            
            self.state = BusinessState.COMPLETED
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time"].observe(processing_time)
            self.metrics["success_rate"].inc()
            
            return {
                **await self.get_state(),
                "claim_id": str(claim.id),
                "claim_number": claim.number,
                "status": claim.status
            }
            
        except Exception as e:
            logger.error(f"Claim submission error: {e}")
            self.state = BusinessState.FAILED
            self.errors.append(str(e))
            self.metrics["error_count"].inc()
            return await self.get_state()

class PurchaseOrderProcess(BusinessProcess):
    """Purchase order business process"""
    def _setup_validation_rules(self):
        """Setup purchase order validation rules"""
        self.validation_rules = [
            RequiredFieldRule("vendor_id"),
            RequiredFieldRule("items"),
            RangeRule("total_amount", 0.01, 1000000.00)
        ]

    async def process(self, data: Dict) -> Dict:
        """Process purchase order"""
        start_time = datetime.utcnow()
        self.state = BusinessState.PROCESSING
        
        try:
            # Validate data
            if not await self.validate(data):
                self.state = BusinessState.FAILED
                return await self.get_state()
            
            # Create financial service
            financial_service = FinancialService(self.db)
            
            # Create purchase order
            po = await financial_service.create_purchase_order(
                vendor_id=uuid.UUID(data["vendor_id"]),
                items=data["items"],
                currency=data.get("currency", "USD"),
                description=data.get("description"),
                notes=data.get("notes"),
                metadata=data.get("metadata"),
                user_id=self.user_id
            )
            
            self.state = BusinessState.COMPLETED
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time"].observe(processing_time)
            self.metrics["success_rate"].inc()
            
            return {
                **await self.get_state(),
                "po_id": str(po.id),
                "po_number": po.number,
                "status": po.status,
                "total_amount": float(po.total_amount)
            }
            
        except Exception as e:
            logger.error(f"Purchase order error: {e}")
            self.state = BusinessState.FAILED
            self.errors.append(str(e))
            self.metrics["error_count"].inc()
            return await self.get_state()

class BusinessService:
    """Business logic service"""
    def __init__(self, db: Session):
        self.db = db
        self.processes: Dict[str, type[BusinessProcess]] = {
            "claim_submission": ClaimSubmissionProcess,
            "purchase_order": PurchaseOrderProcess
        }

    async def create_process(
        self,
        process_type: str,
        user_id: uuid.UUID
    ) -> BusinessProcess:
        """Create new business process"""
        if process_type not in self.processes:
            raise ValueError(f"Unknown process type: {process_type}")
            
        process_class = self.processes[process_type]
        return process_class(
            self.db,
            uuid.uuid4(),
            user_id
        )

    async def get_metrics(self) -> Dict:
        """Get business metrics"""
        return {
            "processing_time": metrics.business_processing_time._value.get(),
            "validation_time": metrics.business_validation_time._value.get(),
            "error_count": metrics.business_error_count._value.get(),
            "success_rate": metrics.business_success_rate._value.get()
        }

# Create business service factory
def get_business_service(db: Session) -> BusinessService:
    return BusinessService(db)
