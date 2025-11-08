"""
MercadoLibre Product Scraper
Extracts product information from MercadoLibre product pages.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_mercadolibre(url: str) -> dict:
    """
    Scrapes product information from a MercadoLibre product URL.

    Args:
        url: The MercadoLibre product URL

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

        # Create context with realistic settings for Latin America
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='es-ES',
            timezone_id='America/Mexico_City',
            permissions=['geolocation'],
            geolocation={'latitude': 19.4326, 'longitude': -99.1332},  # Mexico City
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
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

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-ES', 'es', 'en']
            });

            window.chrome = {
                runtime: {}
            };
        """)

        try:
            # Navigate to the product page
            print(f"Loading MercadoLibre page: {url}")
            page.goto(url, wait_until='networkidle', timeout=45000)

            # Wait a bit for dynamic content to load
            page.wait_for_timeout(3000)

            print("MercadoLibre page loaded successfully")

            # Extract product title
            try:
                title_selectors = [
                    'h1.ui-pdp-title',
                    '.ui-pdp-title',
                    'h1[class*="title"]',
                    'h1.item-title',
                    '.item-title__primary'
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
                    '.andes-money-amount__fraction',
                    '.price-tag-fraction',
                    'span.andes-money-amount__fraction',
                    '.andes-money-amount--cents-superscript .andes-money-amount__fraction',
                    'span[class*="price-tag-fraction"]',
                    '.price-tag-amount',
                    'meta[itemprop="price"]'
                ]

                for selector in price_selectors:
                    if selector.startswith('meta'):
                        # For meta tags, get the content attribute
                        price_element = page.query_selector(selector)
                        if price_element:
                            price_value = price_element.get_attribute('content')
                            if price_value:
                                # Try to get currency symbol
                                currency_element = page.query_selector('.andes-money-amount__currency-symbol')
                                currency = currency_element.inner_text().strip() if currency_element else '$'
                                result['price'] = f"{currency}{price_value}"
                                break
                    else:
                        price_element = page.query_selector(selector)
                        if price_element:
                            price_text = price_element.inner_text().strip()

                            # Try to get currency symbol
                            currency_element = page.query_selector('.andes-money-amount__currency-symbol')
                            if currency_element:
                                currency = currency_element.inner_text().strip()
                                result['price'] = f"{currency}{price_text}"
                            else:
                                # Check if price already has currency symbol
                                if not any(symbol in price_text for symbol in ['$', '€', '£', 'USD', 'MXN', 'ARS']):
                                    result['price'] = f"${price_text}"
                                else:
                                    result['price'] = price_text
                            break

            except Exception as e:
                print(f"Error extracting price: {e}")

            # Extract main image URL
            try:
                image_selectors = [
                    'figure.ui-pdp-gallery__figure img',
                    '.ui-pdp-image',
                    'img.ui-pdp-gallery__figure__image',
                    '.ui-pdp-gallery__figure img[src]',
                    'figure img[data-zoom]',
                    '.gallery-image img',
                    'img[class*="gallery"]'
                ]

                for selector in image_selectors:
                    image_element = page.query_selector(selector)
                    if image_element:
                        # Try different attributes
                        img_url = (image_element.get_attribute('src') or
                                 image_element.get_attribute('data-src') or
                                 image_element.get_attribute('data-zoom'))

                        if img_url and not img_url.startswith('data:'):
                            result['image_url'] = img_url
                            break

            except Exception as e:
                print(f"Error extracting image: {e}")

        except PlaywrightTimeout:
            print("Error: MercadoLibre page load timeout. Please check the URL and try again.")
        except Exception as e:
            print(f"Error loading MercadoLibre page: {e}")
        finally:
            context.close()
            browser.close()

    return result


def search_mercadolibre(product_title: str, region: str = 'mx', debug: bool = False) -> str:
    """
    Searches for a product on MercadoLibre and returns the URL of the first result.

    Args:
        product_title: The product title to search for
        region: MercadoLibre region (mx, ar, co, br). Defaults to 'mx'
        debug: If True, saves screenshots and prints extra debug info

    Returns:
        URL of the first search result, or empty string if not found
    """
    result_url = ""

    # Map regions to base URLs
    region_urls = {
        'mx': 'https://www.mercadolibre.com.mx',
        'ar': 'https://www.mercadolibre.com.ar',
        'co': 'https://www.mercadolibre.com.co',
        'br': 'https://www.mercadolibre.com.br'
    }

    base_url = region_urls.get(region, region_urls['mx'])

    with sync_playwright() as p:
        # Launch browser with anti-detection settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='es-ES',
        )

        page = context.new_page()

        # Hide webdriver detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        try:
            # Build search URL
            import urllib.parse
            search_query = urllib.parse.quote(product_title)
            search_url = f"{base_url}/jm/search?as_word={search_query}"

            print(f"[DEBUG] Searching MercadoLibre ({region}) for: '{product_title}'")
            print(f"[DEBUG] Search URL: {search_url}")

            page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
            print(f"[DEBUG] Page loaded, waiting for content...")
            page.wait_for_timeout(3000)

            # Take screenshot for debugging
            if debug:
                page.screenshot(path=f'debug_mercadolibre_search_{region}.png')
                print(f"[DEBUG] Screenshot saved: debug_mercadolibre_search_{region}.png")

            # Check page title to see if we got blocked
            page_title = page.title()
            print(f"[DEBUG] Page title: {page_title}")

            # Find first product result
            # Try multiple selectors for product links
            product_link_selectors = [
                '.ui-search-layout__item a.ui-search-link',
                '.ui-search-result__content a',
                'a.ui-search-item__group__element',
                '.ui-search-result a[href*="/ML"]',
                'li.ui-search-layout__item a[href*="/ML"]',
                '.ui-search-result__content-wrapper a'
            ]

            print(f"[DEBUG] Trying {len(product_link_selectors)} different selectors...")
            for i, selector in enumerate(product_link_selectors):
                print(f"[DEBUG] Trying selector {i+1}: {selector}")
                link_element = page.query_selector(selector)
                if link_element:
                    href = link_element.get_attribute('href')
                    if href and '/ML' in href:
                        # MercadoLibre URLs usually contain product ID like MLM123456
                        result_url = href.split('#')[0].split('?')[0]  # Remove anchors and query params
                        print(f"[SUCCESS] Found MercadoLibre product with selector {i+1}: {result_url}")
                        break
                    else:
                        print(f"[DEBUG] Selector {i+1} found link but no ML ID: {href if href else 'None'}")
                else:
                    print(f"[DEBUG] Selector {i+1} found no elements")

            if not result_url:
                print(f"[WARNING] No product found with any selector")
                if debug:
                    # Save HTML for debugging
                    html_content = page.content()
                    with open(f'debug_mercadolibre_search_{region}.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"[DEBUG] HTML saved: debug_mercadolibre_search_{region}.html")

        except PlaywrightTimeout as e:
            print(f"[ERROR] MercadoLibre search timeout: {e}")
            if debug and page:
                try:
                    page.screenshot(path=f'debug_mercadolibre_timeout_{region}.png')
                    print(f"[DEBUG] Timeout screenshot saved")
                except:
                    pass
        except Exception as e:
            print(f"[ERROR] Error searching MercadoLibre: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        finally:
            context.close()
            browser.close()

    return result_url
