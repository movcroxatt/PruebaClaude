"""
Scrapers package for multi-store product scraping.
"""

from .amazon_scraper import scrape_amazon, search_amazon
from .mercadolibre_scraper import scrape_mercadolibre, search_mercadolibre
from .scraper_factory import get_scraper_function, get_supported_stores, get_search_function

__all__ = [
    'scrape_amazon',
    'search_amazon',
    'scrape_mercadolibre',
    'search_mercadolibre',
    'get_scraper_function',
    'get_supported_stores',
    'get_search_function'
]
