#!/usr/bin/env python3
"""
FastAPI Server for Amazon Price Scraper
API endpoints for scraping Amazon product information
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import the scraper function
from scraper import scrape_amazon_product

# Create FastAPI app instance
app = FastAPI(
    title="Amazon Price Scraper API",
    description="API for scraping Amazon product information",
    version="1.0.0"
)

# Thread pool for running blocking scraper operations
executor = ThreadPoolExecutor(max_workers=3)


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
async def scrape_product(request: ScrapeRequest):
    """
    Scrape Amazon product information

    This endpoint accepts an Amazon product URL and returns the scraped data
    including title, price, and main image URL.

    Args:
        request: ScrapeRequest object containing the URL to scrape

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
