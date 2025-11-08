#!/usr/bin/env python3
"""
Amazon Product Scraper
Extracts product information from Amazon product pages.
"""

import sys
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_amazon_product(url: str) -> dict:
    """
    Scrapes product information from an Amazon product URL.

    Args:
        url: The Amazon product URL

    Returns:
        Dictionary containing title, price, and image_url
    """
    result = {
        'title': None,
        'price': None,
        'image_url': None
    }

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set a realistic user agent to avoid detection
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        try:
            # Navigate to the product page
            print(f"Loading page: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)

            # Wait a bit for dynamic content to load
            page.wait_for_timeout(2000)

            # Extract product title
            try:
                title_selectors = [
                    '#productTitle',
                    'h1#title',
                    'h1.product-title',
                    'span#productTitle'
                ]

                for selector in title_selectors:
                    title_element = page.query_selector(selector)
                    if title_element:
                        result['title'] = title_element.inner_text().strip()
                        break

            except Exception as e:
                print(f"Error extracting title: {e}")

            # Extract price
            try:
                price_selectors = [
                    'span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay span.a-offscreen',
                    'span.a-price span.a-offscreen',
                    '#priceblock_ourprice',
                    '#priceblock_dealprice',
                    '#price_inside_buybox',
                    '.a-price .a-offscreen',
                    'span[data-a-color="price"] span.a-offscreen'
                ]

                for selector in price_selectors:
                    price_element = page.query_selector(selector)
                    if price_element:
                        result['price'] = price_element.inner_text().strip()
                        break

            except Exception as e:
                print(f"Error extracting price: {e}")

            # Extract main image URL
            try:
                image_selectors = [
                    '#landingImage',
                    '#imgBlkFront',
                    '#main-image',
                    'img.a-dynamic-image',
                    '#imageBlock img'
                ]

                for selector in image_selectors:
                    image_element = page.query_selector(selector)
                    if image_element:
                        # Try to get the src or data-old-hires attribute
                        img_url = image_element.get_attribute('src')
                        if not img_url or 'data:image' in img_url:
                            # Try alternative attributes for high-res images
                            img_url = (image_element.get_attribute('data-old-hires') or
                                     image_element.get_attribute('data-a-dynamic-image'))

                        if img_url:
                            # If data-a-dynamic-image, it's a JSON object, extract first URL
                            if img_url.startswith('{'):
                                import json
                                try:
                                    img_data = json.loads(img_url)
                                    img_url = list(img_data.keys())[0]
                                except:
                                    pass

                            result['image_url'] = img_url
                            break

            except Exception as e:
                print(f"Error extracting image: {e}")

        except PlaywrightTimeout:
            print("Error: Page load timeout. Please check the URL and try again.")
        except Exception as e:
            print(f"Error loading page: {e}")
        finally:
            browser.close()

    return result


def main():
    """Main function to handle command-line arguments and run the scraper."""
    parser = argparse.ArgumentParser(
        description='Scrape product information from Amazon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scraper.py "https://www.amazon.com/dp/B08N5WRWNW"
  python scraper.py https://www.amazon.com/dp/PRODUCT_ID
        '''
    )

    parser.add_argument(
        'url',
        type=str,
        help='Amazon product URL to scrape'
    )

    args = parser.parse_args()

    # Validate URL
    if 'amazon' not in args.url.lower():
        print("Warning: This doesn't appear to be an Amazon URL")

    # Run the scraper
    print("=" * 60)
    print("Amazon Product Scraper")
    print("=" * 60)

    product_data = scrape_amazon_product(args.url)

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    if product_data['title']:
        print(f"\nTitle: {product_data['title']}")
    else:
        print("\nTitle: NOT FOUND")

    if product_data['price']:
        print(f"\nPrice: {product_data['price']}")
    else:
        print("\nPrice: NOT FOUND")

    if product_data['image_url']:
        print(f"\nImage URL: {product_data['image_url']}")
    else:
        print("\nImage URL: NOT FOUND")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
