"""CRUD operations for database models."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas


def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Get a single item by ID."""
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[models.CategoryEnum] = None,
    record_type: Optional[models.RecordTypeEnum] = None
) -> list[models.Item]:
    """Get a list of items with pagination and optional filtering."""
    query = db.query(models.Item)
    
    # Apply filters if provided
    if category is not None:
        query = query.filter(models.Item.category == category)
    if record_type is not None:
        query = query.filter(models.Item.record_type == record_type)
    
    return query.offset(skip).limit(limit).all()


def get_items_count(
    db: Session,
    category: Optional[models.CategoryEnum] = None,
    record_type: Optional[models.RecordTypeEnum] = None
) -> int:
    """Get total count of items with optional filtering."""
    query = db.query(func.count(models.Item.id))
    
    # Apply filters if provided
    if category is not None:
        query = query.filter(models.Item.category == category)
    if record_type is not None:
        query = query.filter(models.Item.record_type == record_type)
    
    return query.scalar()


def create_item(db: Session, item: schemas.ItemCreate, photo_url: Optional[str] = None) -> models.Item:
    """Create a new item."""
    db_item = models.Item(
        name=item.name,
        description=item.description,
        category=item.category,
        record_type=item.record_type,
        sum=item.sum,
        photo_url=photo_url
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate) -> Optional[models.Item]:
    """Update an existing item."""
    db_item = get_item(db, item_id)
    if db_item is None:
        return None
    
    # Update only provided fields
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item."""
    db_item = get_item(db, item_id)
    if db_item is None:
        return False
    
    db.delete(db_item)
    db.commit()
    return True
