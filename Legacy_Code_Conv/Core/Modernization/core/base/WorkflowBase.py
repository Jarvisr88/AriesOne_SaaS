"""
Workflow Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides base classes for workflow management.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, TypeVar

from pydantic import BaseModel, Field, validator

from ..utils.logging import CoreLogger
from .EntityBase import EntityBase

logger = CoreLogger(__name__)
T = TypeVar('T', bound=EntityBase)


class WorkflowStatus(str, Enum):
    """Workflow status enum."""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class WorkflowTransition(BaseModel):
    """Base model for workflow transitions."""
    from_status: WorkflowStatus = Field(..., description="Source status")
    to_status: WorkflowStatus = Field(..., description="Target status")
    action: str = Field(..., description="Transition action")
    requires_permissions: Set[str] = Field(
        default_factory=set,
        description="Required permissions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class WorkflowDefinition(BaseModel):
    """Base model for workflow definitions."""
    id: str = Field(..., description="Workflow ID")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    entity_type: Type[T] = Field(..., description="Associated entity type")
    initial_status: WorkflowStatus = Field(
        default=WorkflowStatus.DRAFT,
        description="Initial status"
    )
    transitions: List[WorkflowTransition] = Field(
        default_factory=list,
        description="Allowed transitions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    version: str = Field(default="1.0.0", description="Workflow version")
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time."""
        return datetime.utcnow()


class WorkflowInstance(BaseModel):
    """Base model for workflow instances."""
    id: str = Field(..., description="Instance ID")
    workflow_id: str = Field(..., description="Workflow definition ID")
    entity_id: str = Field(..., description="Associated entity ID")
    current_status: WorkflowStatus = Field(..., description="Current status")
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Status history"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time."""
        return datetime.utcnow()


class WorkflowContextBase(ABC):
    """Base class for workflow context."""
    
    @abstractmethod
    async def get_user_permissions(self) -> Set[str]:
        """Get current user's permissions."""
        pass
    
    @abstractmethod
    async def get_entity(self, entity_id: str) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def save_entity(self, entity: T) -> T:
        """Save entity."""
        pass


class WorkflowValidatorBase(ABC):
    """Base class for workflow validators."""
    
    @abstractmethod
    async def validate_transition(self, workflow: WorkflowDefinition,
                                instance: WorkflowInstance,
                                transition: WorkflowTransition,
                                context: WorkflowContextBase) -> bool:
        """Validate workflow transition."""
        try:
            # Check if transition is allowed
            if instance.current_status != transition.from_status:
                return False
            
            # Check permissions
            if transition.requires_permissions:
                user_permissions = await context.get_user_permissions()
                if not transition.requires_permissions.intersection(user_permissions):
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Transition validation failed: {str(e)}")
            return False


class WorkflowExecutorBase(ABC):
    """Base class for workflow executors."""
    
    @abstractmethod
    async def execute_transition(self, workflow: WorkflowDefinition,
                               instance: WorkflowInstance,
                               transition: WorkflowTransition,
                               context: WorkflowContextBase) -> WorkflowInstance:
        """Execute workflow transition."""
        try:
            # Update status
            old_status = instance.current_status
            instance.current_status = transition.to_status
            
            # Add to history
            instance.history.append({
                "from_status": old_status,
                "to_status": transition.to_status,
                "action": transition.action,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": transition.metadata
            })
            
            # Update timestamp
            instance.updated_at = datetime.utcnow()
            
            return instance
        except Exception as e:
            logger.error(f"Transition execution failed: {str(e)}")
            raise


class WorkflowRepositoryBase(ABC):
    """Base class for workflow repositories."""
    
    @abstractmethod
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID."""
        pass
    
    @abstractmethod
    async def save_workflow(self,
                          workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Save workflow definition."""
        pass
    
    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow definition."""
        pass
    
    @abstractmethod
    async def list_workflows(
        self,
        entity_type: Optional[Type[T]] = None
    ) -> List[WorkflowDefinition]:
        """List workflow definitions."""
        pass
    
    @abstractmethod
    async def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID."""
        pass
    
    @abstractmethod
    async def save_instance(self,
                          instance: WorkflowInstance) -> WorkflowInstance:
        """Save workflow instance."""
        pass
    
    @abstractmethod
    async def delete_instance(self, instance_id: str) -> bool:
        """Delete workflow instance."""
        pass
    
    @abstractmethod
    async def list_instances(
        self,
        workflow_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None
    ) -> List[WorkflowInstance]:
        """List workflow instances."""
        pass


class WorkflowServiceBase(ABC):
    """Base class for workflow services."""
    
    def __init__(self, repository: WorkflowRepositoryBase,
                 validator: WorkflowValidatorBase,
                 executor: WorkflowExecutorBase):
        """Initialize workflow service."""
        self.repository = repository
        self.validator = validator
        self.executor = executor
    
    @abstractmethod
    async def start_workflow(self, workflow_id: str, entity_id: str,
                           context: WorkflowContextBase) -> WorkflowInstance:
        """Start new workflow instance."""
        try:
            # Get workflow definition
            workflow = await self.repository.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Create instance
            instance = WorkflowInstance(
                id=str(hash(f"{workflow_id}_{entity_id}_{datetime.utcnow().isoformat()}")),
                workflow_id=workflow_id,
                entity_id=entity_id,
                current_status=workflow.initial_status
            )
            
            # Save instance
            return await self.repository.save_instance(instance)
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            raise
    
    @abstractmethod
    async def transition_workflow(self, instance_id: str, action: str,
                                context: WorkflowContextBase) -> WorkflowInstance:
        """Transition workflow instance."""
        try:
            # Get instance and workflow
            instance = await self.repository.get_instance(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} not found")
            
            workflow = await self.repository.get_workflow(instance.workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {instance.workflow_id} not found")
            
            # Find transition
            transition = next(
                (t for t in workflow.transitions
                 if t.from_status == instance.current_status
                 and t.action == action),
                None
            )
            if not transition:
                raise ValueError(f"Invalid transition: {action}")
            
            # Validate transition
            if not await self.validator.validate_transition(
                workflow, instance, transition, context
            ):
                raise ValueError(f"Invalid transition: {action}")
            
            # Execute transition
            updated_instance = await self.executor.execute_transition(
                workflow, instance, transition, context
            )
            
            # Save instance
            return await self.repository.save_instance(updated_instance)
        except Exception as e:
            logger.error(f"Failed to transition workflow: {str(e)}")
            raise
