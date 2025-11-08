"""
Scrapers package for multi-store product scraping.
"""

from .amazon_scraper import scrape_amazon
from .mercadolibre_scraper import scrape_mercadolibre
from .scraper_factory import get_scraper_function, get_supported_stores

__all__ = ['scrape_amazon', 'scrape_mercadolibre', 'get_scraper_function', 'get_supported_stores']
