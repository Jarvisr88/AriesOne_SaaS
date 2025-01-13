"""
Form Entity Service Module

This module provides services for form entity maintenance and management.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar, Callable
from ..models.form_entity import (
    FormEntity,
    FormEntityCollection,
    EntityState,
    EntityValidation,
    ValidationResult,
    ValidationSeverity,
    EntityAudit
)
from .base_service import BaseService
from fastapi import HTTPException
from datetime import datetime
import uuid

T = TypeVar('T')

class FormEntityService(BaseService, Generic[T]):
    """Service for managing form entities"""
    
    def __init__(self):
        """Initialize form entity service"""
        self._collections: Dict[str, FormEntityCollection[T]] = {}
        self._validators: Dict[str, List[Callable[[FormEntity[T]], List[ValidationResult]]]] = {}
    
    async def create_collection(self) -> str:
        """
        Create a new entity collection.
        
        Returns:
            Collection ID
        """
        collection_id = str(uuid.uuid4())
        self._collections[collection_id] = FormEntityCollection[T]()
        return collection_id
    
    async def add_entity(
        self,
        collection_id: str,
        data: T,
        user_id: str
    ) -> FormEntity[T]:
        """
        Add a new entity to a collection.
        
        Args:
            collection_id: ID of the collection
            data: Entity data
            user_id: ID of the user creating the entity
            
        Returns:
            Created entity
            
        Raises:
            HTTPException: If collection is not found
        """
        collection = await self._get_collection(collection_id)
        
        # Create entity
        entity = FormEntity[T](
            id=str(uuid.uuid4()),
            state=EntityState.NEW,
            data=data,
            audit=EntityAudit(
                created_at=datetime.utcnow(),
                created_by=user_id,
                version=1
            )
        )
        
        # Validate entity
        await self._validate_entity(entity)
        
        # Add to collection
        collection.add_entity(entity)
        return entity
    
    async def update_entity(
        self,
        collection_id: str,
        entity_id: str,
        data: T,
        user_id: str
    ) -> FormEntity[T]:
        """
        Update an existing entity.
        
        Args:
            collection_id: ID of the collection
            entity_id: ID of the entity to update
            data: Updated entity data
            user_id: ID of the user updating the entity
            
        Returns:
            Updated entity
            
        Raises:
            HTTPException: If entity is not found
        """
        collection = await self._get_collection(collection_id)
        entity = collection.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found: {entity_id}"
            )
        
        # Update entity
        entity.data = data
        entity.state = EntityState.MODIFIED
        entity.audit.modified_at = datetime.utcnow()
        entity.audit.modified_by = user_id
        entity.audit.version += 1
        
        # Validate entity
        await self._validate_entity(entity)
        
        # Update collection
        collection.add_entity(entity)
        return entity
    
    async def delete_entity(
        self,
        collection_id: str,
        entity_id: str
    ):
        """
        Mark an entity as deleted.
        
        Args:
            collection_id: ID of the collection
            entity_id: ID of the entity to delete
            
        Raises:
            HTTPException: If entity is not found
        """
        collection = await self._get_collection(collection_id)
        entity = collection.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found: {entity_id}"
            )
        
        entity.state = EntityState.DELETED
        collection.add_entity(entity)
    
    async def get_entity(
        self,
        collection_id: str,
        entity_id: str
    ) -> Optional[FormEntity[T]]:
        """
        Get an entity by ID.
        
        Args:
            collection_id: ID of the collection
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity if found, None otherwise
            
        Raises:
            HTTPException: If collection is not found
        """
        collection = await self._get_collection(collection_id)
        return collection.get_entity(entity_id)
    
    async def get_modified_entities(
        self,
        collection_id: str
    ) -> List[FormEntity[T]]:
        """
        Get all modified entities in a collection.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            List of modified entities
            
        Raises:
            HTTPException: If collection is not found
        """
        collection = await self._get_collection(collection_id)
        return collection.get_modified_entities()
    
    def add_validator(
        self,
        entity_type: str,
        validator: Callable[[FormEntity[T]], List[ValidationResult]]
    ):
        """
        Add a validator for an entity type.
        
        Args:
            entity_type: Type of entity to validate
            validator: Validation function
        """
        if entity_type not in self._validators:
            self._validators[entity_type] = []
        self._validators[entity_type].append(validator)
    
    async def _get_collection(
        self,
        collection_id: str
    ) -> FormEntityCollection[T]:
        """
        Get a collection by ID.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            FormEntityCollection instance
            
        Raises:
            HTTPException: If collection is not found
        """
        collection = self._collections.get(collection_id)
        if not collection:
            raise HTTPException(
                status_code=404,
                detail=f"Collection not found: {collection_id}"
            )
        return collection
    
    async def _validate_entity(self, entity: FormEntity[T]):
        """
        Validate an entity using registered validators.
        
        Args:
            entity: Entity to validate
        """
        results = []
        entity_type = type(entity.data).__name__
        
        if entity_type in self._validators:
            for validator in self._validators[entity_type]:
                results.extend(validator(entity))
        
        entity.validation = EntityValidation(
            is_valid=not any(
                r.severity == ValidationSeverity.ERROR
                for r in results
            ),
            results=results
        )
