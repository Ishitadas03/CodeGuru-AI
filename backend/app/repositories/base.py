from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async repository providing standard CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key ID."""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Fetch multiple records with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, *, obj_in: dict[str, Any] | Any) -> ModelType:
        """Insert a new record into the database."""
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            # Handle Pydantic model
            db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: ModelType, obj_in: dict[str, Any] | Any) -> ModelType:
        """Update an existing record in the database."""
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, *, id: Any) -> Optional[ModelType]:
        """Delete a record from the database by ID."""
        obj = await self.get(id=id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
