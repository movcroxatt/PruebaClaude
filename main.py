#!/usr/bin/env python3
"""
FastAPI Server for Amazon Price Scraper
API endpoints for scraping Amazon product information
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
from datetime import datetime
from sqlmodel import Session, select

# Import the scraper function
from scraper import scrape_amazon_product

# Import database models and functions
from database import create_db_and_tables, get_session
from models import Product, PriceHistory, ProductReadWithHistory, PriceHistoryRead

# Create FastAPI app instance
app = FastAPI(
    title="Amazon Price Scraper API",
    description="API for scraping Amazon product information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for running blocking scraper operations
executor = ThreadPoolExecutor(max_workers=3)


# Startup event to create database tables
@app.on_event("startup")
def on_startup():
    """Initialize database on application startup"""
    create_db_and_tables()


# Helper functions
def parse_price(price_str: Optional[str]) -> Optional[float]:
    """
    Parse price string to float

    Args:
        price_str: Price string like "$14.98" or "14.98"

    Returns:
        Float price or None if parsing fails
    """
    if not price_str:
        return None

    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def simplify_url(url: str) -> str:
    """
    Simplify Amazon URL by removing tracking parameters

    Args:
        url: Full Amazon URL with parameters

    Returns:
        Simplified URL with just the product ID
    """
    # Extract product ID from URL
    match = re.search(r'/dp/([A-Z0-9]+)', url)
    if match:
        product_id = match.group(1)
        return f"https://www.amazon.com/dp/{product_id}"
    return url


# Pydantic models for request/response
class ScrapeRequest(BaseModel):
    """Request model for scraping endpoint"""
    url: str = Field(..., description="Amazon product URL to scrape", example="https://www.amazon.com/dp/B07RJ18VMF")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.amazon.com/dp/B07RJ18VMF"
            }
        }


class ScrapeResponse(BaseModel):
    """Response model for scraping endpoint"""
    success: bool = Field(..., description="Whether the scraping was successful")
    url: str = Field(..., description="The URL that was scraped")
    data: Optional[dict] = Field(None, description="Scraped product data")
    error: Optional[str] = Field(None, description="Error message if scraping failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "url": "https://www.amazon.com/dp/B07RJ18VMF",
                "data": {
                    "title": "CeraVe Hydrating Facial Cleanser",
                    "price": "$14.98",
                    "image_url": "https://m.media-amazon.com/images/I/..."
                },
                "error": None
            }
        }


@app.get("/")
async def root():
    """
    Root endpoint - Hello World

    Returns:
        dict: Simple greeting message
    """
    return {
        "message": "Hola Mundo",
        "status": "success",
        "api": "Amazon Price Scraper",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: API health status
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }


@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_product(request: ScrapeRequest, session: Session = Depends(get_session)):
    """
    Scrape Amazon product information and save to database

    This endpoint accepts an Amazon product URL, scrapes the data,
    saves it to the database, and returns the scraped information.

    Args:
        request: ScrapeRequest object containing the URL to scrape
        session: Database session (injected by FastAPI)

    Returns:
        ScrapeResponse: Object containing the scraped data or error information

    Raises:
        HTTPException: If the URL is invalid or scraping fails critically
    """
    # Validate URL contains 'amazon'
    if 'amazon' not in request.url.lower():
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Please provide a valid Amazon product URL."
        )

    try:
        # Run the blocking scraper function in a thread pool
        loop = asyncio.get_event_loop()
        scraped_data = await loop.run_in_executor(
            executor,
            scrape_amazon_product,
            request.url
        )

        # Check if any data was scraped
        has_data = any([
            scraped_data.get('title'),
            scraped_data.get('price'),
            scraped_data.get('image_url')
        ])

        if not has_data:
            return ScrapeResponse(
                success=False,
                url=request.url,
                data=scraped_data,
                error="No data could be extracted from the page. The page might be blocked or the URL is invalid."
            )

        # Save to database
        try:
            # Simplify URL for consistent storage
            base_url = simplify_url(request.url)

            # Check if product already exists
            statement = select(Product).where(Product.base_url == base_url)
            existing_product = session.exec(statement).first()

            if existing_product:
                # Update existing product
                existing_product.name = scraped_data.get('title') or existing_product.name
                existing_product.updated_at = datetime.utcnow()
                product = existing_product
            else:
                # Create new product
                product = Product(
                    name=scraped_data.get('title') or "Unknown Product",
                    base_url=base_url
                )
                session.add(product)

            session.commit()
            session.refresh(product)

            # Parse and save price history
            price_float = parse_price(scraped_data.get('price'))
            if price_float is not None:
                price_history = PriceHistory(
                    product_id=product.id,
                    store_name="Amazon.com",
                    price=price_float
                )
                session.add(price_history)
                session.commit()

            # Add database info to response
            scraped_data['product_id'] = product.id
            scraped_data['saved_to_database'] = True

            # Fetch complete price history for this product
            price_statement = select(PriceHistory).where(
                PriceHistory.product_id == product.id
            ).order_by(PriceHistory.timestamp.desc())
            price_history = session.exec(price_statement).all()

            # Convert to list of dicts for JSON response
            scraped_data['price_history'] = [
                {
                    'id': ph.id,
                    'product_id': ph.product_id,
                    'store_name': ph.store_name,
                    'price': ph.price,
                    'timestamp': ph.timestamp.isoformat()
                }
                for ph in price_history
            ]

        except Exception as db_error:
            # If database save fails, log it but still return scraped data
            print(f"Database error: {db_error}")
            scraped_data['saved_to_database'] = False
            scraped_data['database_error'] = str(db_error)

        return ScrapeResponse(
            success=True,
            url=request.url,
            data=scraped_data,
            error=None
        )

    except Exception as e:
        return ScrapeResponse(
            success=False,
            url=request.url,
            data=None,
            error=f"Scraping failed: {str(e)}"
        )


@app.get("/api/product/{product_id}", response_model=ProductReadWithHistory)
async def get_product(product_id: int, session: Session = Depends(get_session)):
    """
    Get product information with price history

    Retrieves a product by ID including all its price history entries,
    sorted by timestamp (newest first).

    Args:
        product_id: The product ID to retrieve
        session: Database session (injected by FastAPI)

    Returns:
        ProductReadWithHistory: Product with complete price history

    Raises:
        HTTPException: 404 if product not found
    """
    # Query product with price history
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found"
        )

    # Query price history for this product, sorted by timestamp descending
    price_statement = select(PriceHistory).where(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.timestamp.desc())

    price_history = session.exec(price_statement).all()

    # Convert to response model
    price_history_reads = [
        PriceHistoryRead(
            id=ph.id,
            product_id=ph.product_id,
            store_name=ph.store_name,
            price=ph.price,
            timestamp=ph.timestamp
        )
        for ph in price_history
    ]

    return ProductReadWithHistory(
        id=product.id,
        name=product.name,
        base_url=product.base_url,
        created_at=product.created_at,
        updated_at=product.updated_at,
        price_history=price_history_reads
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
