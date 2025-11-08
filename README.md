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

**3. Scrape Amazon product (NEW)**
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
    "image_url": "https://m.media-amazon.com/images/I/..."
  },
  "error": null
}
```

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

**4. Interactive API documentation**

Visit in your browser:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using the API from different clients

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape",
    json={"url": "https://www.amazon.com/dp/B07RJ18VMF"}
)
data = response.json()
print(data)
```

**JavaScript (Node.js):**
```javascript
const response = await fetch('http://localhost:8000/api/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.amazon.com/dp/B07RJ18VMF' })
});
const data = await response.json();
console.log(data);
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B07RJ18VMF"}'
```

## Database Models

The project uses SQLModel (Pydantic + SQLAlchemy) for data persistence with SQLite.

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

```bash
# Create database tables
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
