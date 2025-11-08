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
        # Launch browser with anti-detection settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )

        page = context.new_page()

        # Hide webdriver detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Overwrite the `languages` property to use a custom getter.
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Chrome specific
            window.chrome = {
                runtime: {}
            };
        """)

        try:
            # Navigate to the product page
            print(f"Loading page: {url}")
            page.goto(url, wait_until='networkidle', timeout=45000)

            # Wait a bit for dynamic content to load
            page.wait_for_timeout(3000)

            print("Page loaded successfully")

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
            context.close()
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
