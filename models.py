"""
Database models for Amazon Price Scraper
Using SQLModel for ORM with FastAPI integration
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Product(SQLModel, table=True):
    """
    Product model to store Amazon product information

    Attributes:
        id: Primary key, auto-incremented
        name: Product name/title
        base_url: Base Amazon product URL (without tracking parameters)
        created_at: Timestamp when product was first added
        updated_at: Timestamp when product was last updated
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="Product name/title")
    base_url: str = Field(unique=True, index=True, description="Amazon product URL")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Relationship to price history
    price_history: List["PriceHistory"] = Relationship(back_populates="product")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "CeraVe Hydrating Facial Cleanser",
                "base_url": "https://www.amazon.com/dp/B07RJ18VMF",
                "created_at": "2025-01-08T12:00:00",
                "updated_at": "2025-01-08T12:00:00"
            }
        }


class PriceHistory(SQLModel, table=True):
    """
    PriceHistory model to track price changes over time

    Attributes:
        id: Primary key, auto-incremented
        product_id: Foreign key to Product
        store_name: Name of the store (e.g., "Amazon.com", "Amazon.es")
        price: Product price at the time of scraping
        timestamp: When the price was recorded
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", description="Reference to product")
    store_name: str = Field(default="Amazon.com", description="Store/marketplace name")
    price: float = Field(description="Product price")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Price record timestamp")

    # Relationship to product
    product: Optional[Product] = Relationship(back_populates="price_history")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "store_name": "Amazon.com",
                "price": 14.98,
                "timestamp": "2025-01-08T12:00:00"
            }
        }


# Pydantic models for API requests/responses (without SQLModel table=True)
class ProductCreate(SQLModel):
    """Schema for creating a new product"""
    name: str
    base_url: str


class ProductRead(SQLModel):
    """Schema for reading product data"""
    id: int
    name: str
    base_url: str
    created_at: datetime
    updated_at: datetime


class ProductReadWithHistory(ProductRead):
    """Schema for reading product with price history"""
    price_history: List["PriceHistoryRead"] = []


class PriceHistoryCreate(SQLModel):
    """Schema for creating a new price history entry"""
    product_id: int
    store_name: str = "Amazon.com"
    price: float


class PriceHistoryRead(SQLModel):
    """Schema for reading price history data"""
    id: int
    product_id: int
    store_name: str
    price: float
    timestamp: datetime
