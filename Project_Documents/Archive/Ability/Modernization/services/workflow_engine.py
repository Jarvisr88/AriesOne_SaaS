"""
Workflow Engine Service Module

This module provides a flexible workflow engine for managing business processes.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Callable
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from fastapi import HTTPException

class WorkflowState(str, Enum):
    """Workflow state enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"

class WorkflowStepType(str, Enum):
    """Workflow step type enumeration"""
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    SUBPROCESS = "subprocess"
    EVENT = "event"
    TIMER = "timer"

class WorkflowStep(BaseModel):
    """Workflow step definition"""
    step_id: UUID = Field(default_factory=uuid4)
    name: str
    type: WorkflowStepType
    description: Optional[str] = None
    handler: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    next_steps: List[UUID] = Field(default_factory=list)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowDefinition(BaseModel):
    """Workflow definition"""
    workflow_id: UUID = Field(default_factory=uuid4)
    name: str
    version: str
    description: Optional[str] = None
    steps: Dict[UUID, WorkflowStep]
    start_step: UUID
    end_steps: List[UUID]
    variables: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowInstance(BaseModel):
    """Workflow instance"""
    instance_id: UUID = Field(default_factory=uuid4)
    workflow_id: UUID
    state: WorkflowState = WorkflowState.PENDING
    current_step: Optional[UUID] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowEngine:
    """Workflow engine service"""
    
    def __init__(self):
        """Initialize workflow engine"""
        self._workflows: Dict[UUID, WorkflowDefinition] = {}
        self._instances: Dict[UUID, WorkflowInstance] = {}
        self._handlers: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}

    async def register_workflow(
        self,
        name: str,
        version: str,
        steps: List[WorkflowStep],
        start_step: UUID,
        end_steps: List[UUID],
        description: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowDefinition:
        """Register a new workflow definition"""
        steps_dict = {step.step_id: step for step in steps}
        
        workflow = WorkflowDefinition(
            name=name,
            version=version,
            description=description,
            steps=steps_dict,
            start_step=start_step,
            end_steps=end_steps,
            variables=variables or {},
            timeout=timeout,
            metadata=metadata or {}
        )
        
        self._workflows[workflow.workflow_id] = workflow
        return workflow

    async def create_instance(
        self,
        workflow_id: UUID,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowInstance:
        """Create a new workflow instance"""
        if workflow_id not in self._workflows:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found: {workflow_id}"
            )
        
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            variables=variables or {},
            metadata=metadata or {}
        )
        
        self._instances[instance.instance_id] = instance
        return instance

    async def start_instance(
        self,
        instance_id: UUID
    ) -> WorkflowInstance:
        """Start a workflow instance"""
        instance = self._instances.get(instance_id)
        if not instance:
            raise HTTPException(
                status_code=404,
                detail=f"Instance not found: {instance_id}"
            )
        
        workflow = self._workflows.get(instance.workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found: {instance.workflow_id}"
            )
        
        instance.state = WorkflowState.ACTIVE
        instance.current_step = workflow.start_step
        instance.started_at = datetime.utcnow()
        
        # Execute first step
        await self._execute_step(instance, workflow.steps[workflow.start_step])
        
        return instance

    async def register_handler(
        self,
        handler_name: str,
        handler: Callable
    ):
        """Register a step handler"""
        self._handlers[handler_name] = handler

    async def register_event_handler(
        self,
        event_type: str,
        handler: Callable
    ):
        """Register an event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def handle_event(
        self,
        instance_id: UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Handle an external event"""
        instance = self._instances.get(instance_id)
        if not instance:
            raise HTTPException(
                status_code=404,
                detail=f"Instance not found: {instance_id}"
            )
        
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(instance, event_data)
                except Exception as e:
                    instance.error = {
                        "step": instance.current_step,
                        "error": str(e),
                        "timestamp": datetime.utcnow()
                    }
                    instance.state = WorkflowState.FAILED
                    raise

    async def _execute_step(
        self,
        instance: WorkflowInstance,
        step: WorkflowStep
    ):
        """Execute a workflow step"""
        try:
            # Get step handler
            handler = self._handlers.get(step.handler)
            if not handler:
                raise ValueError(f"Handler not found: {step.handler}")
            
            # Execute handler
            result = await handler(instance, step.parameters)
            
            # Record in history
            instance.history.append({
                "step_id": step.step_id,
                "step_name": step.name,
                "result": result,
                "timestamp": datetime.utcnow()
            })
            
            # Handle completion
            workflow = self._workflows[instance.workflow_id]
            if step.step_id in workflow.end_steps:
                instance.state = WorkflowState.COMPLETED
                instance.completed_at = datetime.utcnow()
            else:
                # Move to next step(s)
                for next_step_id in step.next_steps:
                    next_step = workflow.steps[next_step_id]
                    await self._execute_step(instance, next_step)
                    
        except Exception as e:
            instance.error = {
                "step": step.step_id,
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
            instance.state = WorkflowState.FAILED
            raise
