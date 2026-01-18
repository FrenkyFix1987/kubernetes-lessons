"""SQLAlchemy database models."""
import enum
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Numeric
from sqlalchemy.sql import func
from app.database import Base


class CategoryEnum(str, enum.Enum):
    """Category enumeration for items."""
    FOOD = "food"
    CAR = "car"
    RENT = "rent"


class RecordTypeEnum(str, enum.Enum):
    """Record type enumeration for financial tracking."""
    INCOME = "income"
    EXPENSE = "expense"


class Item(Base):
    """Item model for storing financial records."""
    
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(CategoryEnum), nullable=True, index=True)
    record_type = Column(Enum(RecordTypeEnum), nullable=False, index=True)
    sum = Column(Numeric(precision=10, scale=2), nullable=False)
    photo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', type='{self.record_type}', sum={self.sum})>"
