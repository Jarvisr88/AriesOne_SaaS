from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base_class import Base
from app.core.logging import logger

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self,
        db: AsyncSession,
        id: Any,
        for_update: bool = False
    ) -> Optional[ModelType]:
        """Get a single record by id"""
        try:
            query = select(self.model).filter(self.model.id == id)
            if for_update:
                query = query.with_for_update()
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: List[str] = None
    ) -> List[ModelType]:
        """Get multiple records with filtering and ordering"""
        try:
            query = select(self.model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            
            if order_by:
                for field in order_by:
                    direction = "asc"
                    if field.startswith("-"):
                        direction = "desc"
                        field = field[1:]
                    if hasattr(self.model, field):
                        query = query.order_by(
                            getattr(getattr(self.model, field), direction)()
                        )
            
            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new record"""
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        try:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise

    async def delete(
        self,
        db: AsyncSession,
        *,
        id: Any
    ) -> Optional[ModelType]:
        """Delete a record by id"""
        try:
            obj = await self.get(db, id)
            if obj:
                await db.delete(obj)
                await db.flush()
            return obj
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise

    async def count(
        self,
        db: AsyncSession,
        filters: Dict[str, Any] = None
    ) -> int:
        """Count records with optional filtering"""
        try:
            query = select(func.count()).select_from(self.model)
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            result = await db.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise

    async def exists(
        self,
        db: AsyncSession,
        id: Any
    ) -> bool:
        """Check if a record exists by id"""
        try:
            query = select(func.count()).select_from(self.model).filter(
                self.model.id == id
            )
            result = await db.execute(query)
            return result.scalar_one() > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            raise

    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """Create multiple records in bulk"""
        try:
            db_objs = []
            for obj_in in objs_in:
                obj_in_data = jsonable_encoder(obj_in)
                db_obj = self.model(**obj_in_data)
                db_objs.append(db_obj)
            
            db.add_all(db_objs)
            await db.flush()
            for db_obj in db_objs:
                await db.refresh(db_obj)
            return db_objs
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise

    async def bulk_update(
        self,
        db: AsyncSession,
        *,
        objs: List[Tuple[ModelType, Union[UpdateSchemaType, Dict[str, Any]]]]
    ) -> List[ModelType]:
        """Update multiple records in bulk"""
        try:
            updated_objs = []
            for db_obj, obj_in in objs:
                updated_obj = await self.update(db, db_obj=db_obj, obj_in=obj_in)
                updated_objs.append(updated_obj)
            return updated_objs
        except Exception as e:
            logger.error(f"Error bulk updating {self.model.__name__}: {e}")
            raise
