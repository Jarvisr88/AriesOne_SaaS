"""
Form Entity API Endpoints Module

This module provides FastAPI endpoints for form entity maintenance.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Generic, TypeVar
from ..models.form_entity import (
    FormEntity,
    FormEntityCollection,
    EntityState,
    EntityValidation
)
from ..services.form_entity_service import FormEntityService
from ..services.auth_service import get_current_user, User

T = TypeVar('T')
router = APIRouter()

@router.post("/collections", response_model=str)
async def create_collection(
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a new entity collection.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Collection ID
    """
    service = FormEntityService[Dict[str, Any]]()
    return await service.create_collection()

@router.post("/collections/{collection_id}/entities", response_model=FormEntity[T])
async def add_entity(
    collection_id: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> FormEntity[Dict[str, Any]]:
    """
    Add a new entity to a collection.
    
    Args:
        collection_id: ID of the collection
        data: Entity data
        current_user: The current authenticated user
        
    Returns:
        Created entity
    """
    service = FormEntityService[Dict[str, Any]]()
    return await service.add_entity(
        collection_id=collection_id,
        data=data,
        user_id=current_user.id
    )

@router.put("/collections/{collection_id}/entities/{entity_id}", response_model=FormEntity[T])
async def update_entity(
    collection_id: str,
    entity_id: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> FormEntity[Dict[str, Any]]:
    """
    Update an existing entity.
    
    Args:
        collection_id: ID of the collection
        entity_id: ID of the entity to update
        data: Updated entity data
        current_user: The current authenticated user
        
    Returns:
        Updated entity
    """
    service = FormEntityService[Dict[str, Any]]()
    return await service.update_entity(
        collection_id=collection_id,
        entity_id=entity_id,
        data=data,
        user_id=current_user.id
    )

@router.delete("/collections/{collection_id}/entities/{entity_id}")
async def delete_entity(
    collection_id: str,
    entity_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Mark an entity as deleted.
    
    Args:
        collection_id: ID of the collection
        entity_id: ID of the entity to delete
        current_user: The current authenticated user
    """
    service = FormEntityService[Dict[str, Any]]()
    await service.delete_entity(
        collection_id=collection_id,
        entity_id=entity_id
    )

@router.get("/collections/{collection_id}/entities/{entity_id}", response_model=FormEntity[T])
async def get_entity(
    collection_id: str,
    entity_id: str,
    current_user: User = Depends(get_current_user)
) -> FormEntity[Dict[str, Any]]:
    """
    Get an entity by ID.
    
    Args:
        collection_id: ID of the collection
        entity_id: ID of the entity to retrieve
        current_user: The current authenticated user
        
    Returns:
        Entity if found
        
    Raises:
        HTTPException: If entity is not found
    """
    service = FormEntityService[Dict[str, Any]]()
    entity = await service.get_entity(
        collection_id=collection_id,
        entity_id=entity_id
    )
    if not entity:
        raise HTTPException(
            status_code=404,
            detail=f"Entity not found: {entity_id}"
        )
    return entity

@router.get("/collections/{collection_id}/entities/modified", response_model=List[FormEntity[T]])
async def get_modified_entities(
    collection_id: str,
    current_user: User = Depends(get_current_user)
) -> List[FormEntity[Dict[str, Any]]]:
    """
    Get all modified entities in a collection.
    
    Args:
        collection_id: ID of the collection
        current_user: The current authenticated user
        
    Returns:
        List of modified entities
    """
    service = FormEntityService[Dict[str, Any]]()
    return await service.get_modified_entities(collection_id)
