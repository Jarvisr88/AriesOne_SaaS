"""
Business Rules Engine Service Module

This module provides a flexible rules engine for managing business logic.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Callable
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from fastapi import HTTPException

class RuleType(str, Enum):
    """Rule type enumeration"""
    VALIDATION = "validation"
    CALCULATION = "calculation"
    TRANSFORMATION = "transformation"
    DECISION = "decision"
    ACTION = "action"

class RuleOperator(str, Enum):
    """Rule operator enumeration"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES = "matches"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

class RuleCondition(BaseModel):
    """Rule condition definition"""
    field: str
    operator: RuleOperator
    value: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RuleAction(BaseModel):
    """Rule action definition"""
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BusinessRule(BaseModel):
    """Business rule definition"""
    rule_id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    rule_type: RuleType
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RuleExecutionResult(BaseModel):
    """Rule execution result"""
    rule_id: UUID
    success: bool
    actions_executed: List[Dict[str, Any]]
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessRulesEngine:
    """Business rules engine service"""
    
    def __init__(self):
        """Initialize business rules engine"""
        self._rules: Dict[UUID, BusinessRule] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._field_resolvers: Dict[str, Callable] = {}

    async def register_rule(
        self,
        name: str,
        rule_type: RuleType,
        conditions: List[RuleCondition],
        actions: List[RuleAction],
        description: Optional[str] = None,
        priority: int = 0,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BusinessRule:
        """Register a new business rule"""
        rule = BusinessRule(
            name=name,
            description=description,
            rule_type=rule_type,
            conditions=conditions,
            actions=actions,
            priority=priority,
            enabled=enabled,
            metadata=metadata or {}
        )
        
        self._rules[rule.rule_id] = rule
        return rule

    async def register_action_handler(
        self,
        action_type: str,
        handler: Callable
    ):
        """Register an action handler"""
        self._action_handlers[action_type] = handler

    async def register_field_resolver(
        self,
        field_pattern: str,
        resolver: Callable
    ):
        """Register a field resolver"""
        self._field_resolvers[field_pattern] = resolver

    async def evaluate_rules(
        self,
        context: Dict[str, Any],
        rule_type: Optional[RuleType] = None
    ) -> List[RuleExecutionResult]:
        """Evaluate business rules against context"""
        results = []
        
        # Sort rules by priority
        rules = sorted(
            [r for r in self._rules.values() if r.enabled],
            key=lambda x: x.priority,
            reverse=True
        )
        
        # Filter by type if specified
        if rule_type:
            rules = [r for r in rules if r.rule_type == rule_type]
        
        # Evaluate each rule
        for rule in rules:
            try:
                # Check conditions
                conditions_met = await self._evaluate_conditions(
                    rule.conditions,
                    context
                )
                
                if conditions_met:
                    # Execute actions
                    actions_executed = await self._execute_actions(
                        rule.actions,
                        context
                    )
                    
                    results.append(
                        RuleExecutionResult(
                            rule_id=rule.rule_id,
                            success=True,
                            actions_executed=actions_executed
                        )
                    )
                
            except Exception as e:
                results.append(
                    RuleExecutionResult(
                        rule_id=rule.rule_id,
                        success=False,
                        actions_executed=[],
                        error={
                            "message": str(e),
                            "timestamp": datetime.utcnow()
                        }
                    )
                )
        
        return results

    async def _evaluate_conditions(
        self,
        conditions: List[RuleCondition],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate rule conditions"""
        for condition in conditions:
            # Resolve field value
            field_value = await self._resolve_field(condition.field, context)
            
            # Apply operator
            if condition.operator == RuleOperator.EQUALS:
                if field_value != condition.value:
                    return False
            elif condition.operator == RuleOperator.NOT_EQUALS:
                if field_value == condition.value:
                    return False
            elif condition.operator == RuleOperator.GREATER_THAN:
                if not field_value > condition.value:
                    return False
            elif condition.operator == RuleOperator.LESS_THAN:
                if not field_value < condition.value:
                    return False
            elif condition.operator == RuleOperator.CONTAINS:
                if condition.value not in field_value:
                    return False
            elif condition.operator == RuleOperator.NOT_CONTAINS:
                if condition.value in field_value:
                    return False
            elif condition.operator == RuleOperator.MATCHES:
                if not bool(condition.value.match(str(field_value))):
                    return False
            elif condition.operator == RuleOperator.IN:
                if field_value not in condition.value:
                    return False
            elif condition.operator == RuleOperator.NOT_IN:
                if field_value in condition.value:
                    return False
            elif condition.operator == RuleOperator.EXISTS:
                if field_value is None:
                    return False
            elif condition.operator == RuleOperator.NOT_EXISTS:
                if field_value is not None:
                    return False
        
        return True

    async def _execute_actions(
        self,
        actions: List[RuleAction],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute rule actions"""
        results = []
        
        for action in actions:
            handler = self._action_handlers.get(action.action_type)
            if not handler:
                raise ValueError(f"Action handler not found: {action.action_type}")
            
            result = await handler(action.parameters, context)
            results.append({
                "action_type": action.action_type,
                "parameters": action.parameters,
                "result": result,
                "timestamp": datetime.utcnow()
            })
        
        return results

    async def _resolve_field(
        self,
        field: str,
        context: Dict[str, Any]
    ) -> Any:
        """Resolve field value from context"""
        # Check for direct field access
        if field in context:
            return context[field]
        
        # Try field resolvers
        for pattern, resolver in self._field_resolvers.items():
            if bool(pattern.match(field)):
                return await resolver(field, context)
        
        raise ValueError(f"Unable to resolve field: {field}")
