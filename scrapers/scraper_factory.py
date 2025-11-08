"""
Scraper Factory - Detects which store scraper to use based on URL.
"""

from typing import Callable, Optional, List
from urllib.parse import urlparse
from .amazon_scraper import scrape_amazon, search_amazon
from .mercadolibre_scraper import scrape_mercadolibre, search_mercadolibre


def get_scraper_function(url: str) -> Optional[Callable[[str], dict]]:
    """
    Analyzes the URL and returns the appropriate scraper function.

    Args:
        url: The product URL to scrape

    Returns:
        A scraper function (callable) if the store is supported, None otherwise.
    """
    try:
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Detect store based on domain
        if 'amazon.com' in domain or 'amazon.' in domain:
            return scrape_amazon
        elif 'mercadolibre.com' in domain or 'mercadolibre.' in domain or 'mercadolibre.com.' in domain:
            return scrape_mercadolibre

        # Add more stores here in the future:
        # elif 'ebay.com' in domain:
        #     return scrape_ebay
        # elif 'aliexpress.com' in domain:
        #     return scrape_aliexpress

        # Store not supported
        return None

    except Exception as e:
        print(f"Error parsing URL in scraper factory: {e}")
        return None


def get_supported_stores() -> List[str]:
    """
    Returns a list of currently supported store names.

    Returns:
        List of supported store names.
    """
    return [
        'Amazon',
        'MercadoLibre'
        # Add more stores as they are implemented:
        # 'eBay',
        # 'AliExpress',
    ]


def get_search_function(store_name: str) -> Optional[Callable[[str], str]]:
    """
    Returns the appropriate search function for a given store name.

    Args:
        store_name: The name of the store (case-insensitive)

    Returns:
        A search function that takes a product title and returns a product URL,
        or None if the store is not supported.
    """
    store_lower = store_name.lower()

    if 'amazon' in store_lower:
        return search_amazon
    elif 'mercadolibre' in store_lower or 'mercadolivre' in store_lower:
        return search_mercadolibre

    # Add more stores here in the future:
    # elif 'ebay' in store_lower:
    #     return search_ebay

    return None
