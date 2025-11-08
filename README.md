# Amazon Price Scraper

A Python-based price scraper using Playwright to extract product information from Amazon, with a FastAPI REST API.

## Features

- Extracts product title
- Extracts current price
- Extracts main product image URL
- Anti-detection techniques to bypass Amazon's bot protection
- Realistic browser fingerprinting
- Custom HTTP headers and user agent
- **FastAPI REST API** for easy integration
- **SQLModel database** for persistent storage
- **Price history tracking** to monitor price changes over time

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

### Command Line Interface (CLI)

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

### FastAPI REST API

Start the API server:

```bash
# Method 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using python
python main.py
```

The API will be available at: `http://localhost:8000`

#### Available Endpoints:

**1. Root endpoint (Hello World)**
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "message": "Hola Mundo",
  "status": "success",
  "api": "Amazon Price Scraper",
  "version": "1.0.0"
}
```

**2. Health check**
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

**3. Scrape Amazon product (with Database Integration)**
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B07RJ18VMF"}'
```

Response (Success):
```json
{
  "success": true,
  "url": "https://www.amazon.com/dp/B07RJ18VMF",
  "data": {
    "title": "CeraVe Hydrating Facial Cleanser...",
    "price": "$14.98",
    "image_url": "https://m.media-amazon.com/images/I/...",
    "product_id": 1,
    "saved_to_database": true
  },
  "error": null
}
```

**What happens when you scrape:**
1. The product is scraped from Amazon
2. If it's a new product, it's created in the database
3. If it already exists, the product info is updated
4. A new price history entry is added with current price
5. The response includes `product_id` and `saved_to_database` status

Response (Error):
```json
{
  "success": false,
  "url": "https://www.amazon.com/dp/INVALID",
  "data": {
    "title": null,
    "price": null,
    "image_url": null
  },
  "error": "No data could be extracted from the page..."
}
```

**4. Get product with price history**
```bash
curl http://localhost:8000/api/product/1
```

Response:
```json
{
  "id": 1,
  "name": "CeraVe Hydrating Facial Cleanser",
  "base_url": "https://www.amazon.com/dp/B07RJ18VMF",
  "created_at": "2025-11-08T12:00:00",
  "updated_at": "2025-11-08T15:30:00",
  "price_history": [
    {
      "id": 3,
      "product_id": 1,
      "store_name": "Amazon.com",
      "price": 13.99,
      "timestamp": "2025-11-08T15:30:00"
    },
    {
      "id": 2,
      "product_id": 1,
      "store_name": "Amazon.com",
      "price": 14.98,
      "timestamp": "2025-11-07T10:00:00"
    },
    {
      "id": 1,
      "product_id": 1,
      "store_name": "Amazon.com",
      "price": 15.99,
      "timestamp": "2025-11-06T08:00:00"
    }
  ]
}
```

**Features:**
- Returns complete product information
- Includes all price history entries
- Prices sorted by timestamp (newest first)
- Returns 404 if product not found

**5. Interactive API documentation**

Visit in your browser:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using the API from different clients

**Python:**
```python
import requests

# Scrape a product
scrape_response = requests.post(
    "http://localhost:8000/api/scrape",
    json={"url": "https://www.amazon.com/dp/B07RJ18VMF"}
)
scrape_data = scrape_response.json()
product_id = scrape_data['data']['product_id']

# Get product with price history
product_response = requests.get(f"http://localhost:8000/api/product/{product_id}")
product_data = product_response.json()
print(f"Product: {product_data['name']}")
print(f"Price history: {len(product_data['price_history'])} entries")
```

**JavaScript (Node.js):**
```javascript
// Scrape a product
const scrapeResponse = await fetch('http://localhost:8000/api/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.amazon.com/dp/B07RJ18VMF' })
});
const scrapeData = await scrapeResponse.json();
const productId = scrapeData.data.product_id;

// Get product with price history
const productResponse = await fetch(`http://localhost:8000/api/product/${productId}`);
const productData = await productResponse.json();
console.log(`Product: ${productData.name}`);
console.log(`Price history: ${productData.price_history.length} entries`);
```

**cURL:**
```bash
# Scrape a product
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B07RJ18VMF"}'

# Get product with history
curl http://localhost:8000/api/product/1
```

## Database Models

The project uses SQLModel (Pydantic + SQLAlchemy) for data persistence with SQLite.

### Automatic Database Integration

**The API automatically saves all scraped data to the database!**

When you use the `/api/scrape` endpoint:
- Products are automatically created or updated
- Price history is recorded with each scrape
- URLs are normalized (tracking parameters removed)
- Duplicate products are detected by URL

### Schema

**Product Table:**
- `id`: Primary key (auto-increment)
- `name`: Product name/title
- `base_url`: Amazon product URL (unique)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**PriceHistory Table:**
- `id`: Primary key (auto-increment)
- `product_id`: Foreign key to Product
- `store_name`: Store name (e.g., "Amazon.com")
- `price`: Product price at time of scraping
- `timestamp`: When the price was recorded

### Initializing the Database

**The database is automatically initialized when you start the API server!**

The FastAPI app creates all necessary tables on startup, so you don't need to do anything manually.

If you want to initialize the database separately:
```bash
# Create database tables manually
python database.py
```

This creates a SQLite database file `amazon_scraper.db` with the schema.

### Database Usage Example

```python
from sqlmodel import Session, select
from database import engine
from models import Product, PriceHistory

# Create a session
with Session(engine) as session:
    # Create a product
    product = Product(
        name="CeraVe Hydrating Facial Cleanser",
        base_url="https://www.amazon.com/dp/B07RJ18VMF"
    )
    session.add(product)
    session.commit()

    # Add price history
    price = PriceHistory(
        product_id=product.id,
        store_name="Amazon.com",
        price=14.98
    )
    session.add(price)
    session.commit()

    # Query products
    statement = select(Product)
    products = session.exec(statement).all()
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
├── scraper.py          # CLI scraper script
├── main.py             # FastAPI REST API server
├── models.py           # SQLModel database models (Product, PriceHistory)
├── database.py         # Database configuration and session management
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── TESTING_GUIDE.md    # Local testing guide
├── .gitignore          # Git ignore rules
└── amazon_scraper.db   # SQLite database (created on first run)
```
