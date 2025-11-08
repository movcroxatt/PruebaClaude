#!/usr/bin/env python3
"""
FastAPI Server for Amazon Price Scraper
Basic API with Hello World endpoint
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI app instance
app = FastAPI(
    title="Amazon Price Scraper API",
    description="API for scraping Amazon product information",
    version="1.0.0"
)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
