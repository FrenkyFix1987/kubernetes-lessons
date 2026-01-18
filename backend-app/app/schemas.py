"""Pydantic schemas for request/response validation."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models import CategoryEnum, RecordTypeEnum


class ItemBase(BaseModel):
    """Base schema for Item."""
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    category: Optional[CategoryEnum] = Field(None, description="Item category (food, car, rent)")
    record_type: RecordTypeEnum = Field(..., description="Record type (income or expense)")
    sum: Decimal = Field(..., gt=0, description="Amount (must be positive)")
    
    @field_validator('sum')
    @classmethod
    def validate_sum(cls, v: Decimal) -> Decimal:
        """Validate that sum is positive."""
        if v <= 0:
            raise ValueError('Sum must be strictly positive')
        return v


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    category: Optional[CategoryEnum] = Field(None, description="Item category (food, car, rent)")
    record_type: Optional[RecordTypeEnum] = Field(None, description="Record type (income or expense)")
    sum: Optional[Decimal] = Field(None, gt=0, description="Amount (must be positive)")
    
    @field_validator('sum')
    @classmethod
    def validate_sum(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that sum is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Sum must be strictly positive')
        return v


class ItemResponse(ItemBase):
    """Schema for item response."""
    id: int
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ItemList(BaseModel):
    """Schema for paginated item list."""
    items: list[ItemResponse]
    total: int
    skip: int
    limit: int
