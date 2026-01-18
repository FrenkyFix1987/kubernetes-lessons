"""API endpoints for items."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from decimal import Decimal
from app import crud, schemas
from app.database import get_db
from app.models import CategoryEnum, RecordTypeEnum
from app.azure_storage import get_blob_service

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    name: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    category: Optional[CategoryEnum] = Form(None),
    record_type: RecordTypeEnum = Form(...),
    sum: Decimal = Form(..., gt=0),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new financial record with optional photo attachment.
    
    - **name**: Item name (required, 1-255 characters)
    - **description**: Item description (optional)
    - **category**: Category - food, car, or rent (optional)
    - **record_type**: Record type - income or expense (required)
    - **sum**: Amount in currency (required, must be positive)
    - **photo**: Photo attachment (optional, max 10MB, jpg/png/gif/webp)
    """
    # Validate sum
    if sum <= 0:
        raise HTTPException(
            status_code=400,
            detail="Sum must be strictly positive"
        )
    
    # Create item schema for validation
    item_data = schemas.ItemCreate(
        name=name,
        description=description,
        category=category,
        record_type=record_type,
        sum=sum
    )
    
    # Create item in database first (to get ID)
    db_item = crud.create_item(db=db, item=item_data, photo_url=None)
    
    # Upload photo if provided
    photo_url = None
    if photo and photo.filename:
        try:
            blob_service = get_blob_service()
            photo_url = await blob_service.upload_photo(photo, db_item.id)
            
            # Update item with photo URL
            db_item.photo_url = photo_url
            db.commit()
            db.refresh(db_item)
            
        except HTTPException:
            # Re-raise HTTP exceptions (validation errors)
            raise
        except Exception as e:
            # If photo upload fails, keep the record but log the error
            # In production, you might want to delete the record or implement retry logic
            raise HTTPException(
                status_code=500,
                detail=f"Record created but photo upload failed: {str(e)}"
            )
    
    return db_item


@router.get("/", response_model=schemas.ItemList)
def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    category: Optional[CategoryEnum] = Query(None, description="Filter by category (food, car, rent)"),
    record_type: Optional[RecordTypeEnum] = Query(None, description="Filter by record type (income, expense)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of financial records with pagination and optional filtering.
    
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100, max: 1000)
    - **category**: Filter by category - food, car, or rent (optional)
    - **record_type**: Filter by record type - income or expense (optional)
    """
    items = crud.get_items(db=db, skip=skip, limit=limit, category=category, record_type=record_type)
    total = crud.get_items_count(db=db, category=category, record_type=record_type)
    return schemas.ItemList(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{item_id}", response_model=schemas.ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific item by ID.
    
    - **item_id**: ID of the item to retrieve
    """
    db_item = crud.get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return db_item


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing financial record.
    
    - **item_id**: ID of the item to update
    - **name**: New item name (optional)
    - **description**: New item description (optional)
    - **category**: New category - food, car, or rent (optional)
    - **record_type**: New record type - income or expense (optional)
    - **sum**: New amount (optional, must be positive)
    """
    db_item = crud.update_item(db=db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an item.
    
    - **item_id**: ID of the item to delete
    """
    success = crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return None
