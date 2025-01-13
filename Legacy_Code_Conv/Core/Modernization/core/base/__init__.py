"""
Core Base Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides base classes for the core module.
"""

from .EntityBase import EntityBase, EntityMetadata
from .EventHandlerBase import EventHandlerBase, EventMetadata
from .FormBase import (FormDefinition, FormField, FormHandlerBase,
                      FormProcessorBase, FormRepositoryBase, FormValidatorBase)
from .NavigationBase import (NavigationBuilderBase, NavigationContextBase,
                           NavigationItem, NavigationMenu, NavigationRepositoryBase,
                           NavigationServiceBase)
from .RepositoryBase import RepositoryBase, RepositoryError
from .WorkflowBase import (WorkflowContextBase, WorkflowDefinition,
                          WorkflowExecutorBase, WorkflowInstance,
                          WorkflowRepositoryBase, WorkflowServiceBase,
                          WorkflowStatus, WorkflowTransition,
                          WorkflowValidatorBase)

__all__ = [
    # Entity
    'EntityBase',
    'EntityMetadata',
    
    # Event Handler
    'EventHandlerBase',
    'EventMetadata',
    
    # Form
    'FormDefinition',
    'FormField',
    'FormHandlerBase',
    'FormProcessorBase',
    'FormRepositoryBase',
    'FormValidatorBase',
    
    # Navigation
    'NavigationBuilderBase',
    'NavigationContextBase',
    'NavigationItem',
    'NavigationMenu',
    'NavigationRepositoryBase',
    'NavigationServiceBase',
    
    # Repository
    'RepositoryBase',
    'RepositoryError',
    
    # Workflow
    'WorkflowContextBase',
    'WorkflowDefinition',
    'WorkflowExecutorBase',
    'WorkflowInstance',
    'WorkflowRepositoryBase',
    'WorkflowServiceBase',
    'WorkflowStatus',
    'WorkflowTransition',
    'WorkflowValidatorBase'
]
