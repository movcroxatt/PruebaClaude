# Amazon Price Scraper

A Python-based price scraper using Playwright to extract product information from Amazon.

## Features

- Extracts product title
- Extracts current price
- Extracts main product image URL
- Anti-detection techniques to bypass Amazon's bot protection
- Realistic browser fingerprinting
- Custom HTTP headers and user agent

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python scraper.py <AMAZON_PRODUCT_URL>
```

Examples:
```bash
# Simple product URL
python scraper.py "https://www.amazon.com/dp/B07RJ18VMF"

# Full URL with parameters
python scraper.py "https://www.amazon.com/Some-Product-Name/dp/B08N5WRWNW"
```

## Anti-Detection Features

The scraper includes several techniques to avoid detection:

- **Realistic browser configuration**: Viewport, user agent, locale, timezone
- **Header spoofing**: Complete set of realistic HTTP headers
- **WebDriver hiding**: JavaScript injection to mask automation
- **Browser fingerprinting**: Mimics real Chrome browser behavior
- **Network idle waiting**: Ensures page is fully loaded before scraping

## Output

The scraper will display:
```
============================================================
RESULTS
============================================================

Title: [Product Title]

Price: [Product Price]

Image URL: [Product Image URL]

============================================================
```

## Important Notes

- **Network access required**: This scraper needs internet access to work
- **Rate limiting**: Amazon may block excessive requests
- **Success rate**: Not 100% guaranteed due to Amazon's anti-bot measures
- **Legal considerations**: Use responsibly and respect Amazon's Terms of Service

## Troubleshooting

### ERR_TUNNEL_CONNECTION_FAILED
This error indicates network connectivity issues. Ensure:
- You have internet access
- No proxy/firewall is blocking the connection
- Try running from a different network

### Timeout errors
If the page takes too long to load:
- Check your internet speed
- Amazon might be rate limiting your IP
- Try waiting a few minutes between requests

## Project Structure

```
.
├── scraper.py          # Main scraper script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore rules
```
