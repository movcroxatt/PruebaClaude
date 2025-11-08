# Amazon Price Scraper

A Python-based price scraper using Playwright to extract product information from Amazon.

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

Example:
```bash
python scraper.py "https://www.amazon.com/dp/B08N5WRWNW"
```

## Features

- Extracts product title
- Extracts current price
- Extracts main product image URL
