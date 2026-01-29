# Google Maps Scraper

A powerful web scraper for extracting business information from Google Maps with a Flask dashboard for managing and analyzing results.

## Features

- **Google Maps Scraping**: Extract business details including name, address, phone, website, ratings, and reviews
- **Web Dashboard**: Beautiful Flask-based UI to view, manage, and analyze scraped data
- **Website Analysis**: Comprehensive SEO and performance analysis tool
- **MongoDB Integration**: Store and manage scraped data efficiently
- **Email Enrichment**: Find and enrich business email addresses
- **Status Tracking**: Track business outreach status (pending, in progress, approved, rejected)
- **Export Options**: Export data to CSV and Excel formats

## Project Structure

```
scraper/
├── google_maps_scraper/          # Scrapy project
│   ├── spiders/
│   │   ├── gmaps.py             # Google Maps spider
│   │   └── bing.py              # Bing search spider
│   ├── pipelines.py             # MongoDB pipeline
│   ├── settings.py              # Scrapy settings
│   └── items.py                 # Data models
├── app.py                        # Flask dashboard
├── website_analyzer.py           # Website analysis tool
├── enrich_emails.py              # Email enrichment utility
├── csv_to_excel.py               # CSV to Excel converter
├── update_mongo_emails.py        # MongoDB email updater
├── check_mongo.py                # MongoDB connection checker
├── seed_db.py                    # Database seeder
├── scrapy.cfg                    # Scrapy configuration
├── requirements.txt              # Python dependencies
├── run.sh                        # Run script
└── config.py                     # Configuration file
```

## Prerequisites

- Python 3.8+
- MongoDB (running locally on port 27017)
- Playwright browsers

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

3. **Start MongoDB**:
   ```bash
   # Make sure MongoDB is running on localhost:27017
   mongod
   ```

## Usage

### Running the Dashboard

Start the Flask web dashboard:

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

### Running the Scraper

Use the dashboard's search bar to start a scrape, or run manually:

```bash
scrapy crawl gmaps -a query="restaurants in New York"
```

### Utility Scripts

- **Check MongoDB connection**: `python check_mongo.py`
- **Enrich emails**: `python enrich_emails.py`
- **Convert to Excel**: `python csv_to_excel.py input.csv`
- **Update MongoDB emails**: `python update_mongo_emails.py`

## Configuration

Edit `config.py` or `google_maps_scraper/settings.py` to configure:

- MongoDB connection settings
- Scrapy settings (delays, user agents, etc.)
- Playwright browser options

## Dashboard Features

- **Real-time Updates**: View scraped data as it's collected
- **Status Management**: Track outreach status for each business
- **Website Analysis**: Analyze business websites for SEO and performance
- **Search & Filter**: Search through scraped results
- **Export**: Export data to CSV or Excel

## MongoDB Schema

```javascript
{
  name: String,
  address: String,
  phone: String,
  website: String,
  category: String,
  rating: Number,
  reviews: Number,
  emails: [String],
  status: String,  // pending, in_progress, approved, rejected
  analysis: Object  // Website analysis results
}
```

## Production Deployment

1. **Set environment variables** (see `.env.example`):
   - `FLASK_ENV=production` or `ENV=production`
   - `SECRET_KEY` (required) – generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`
   - `MONGO_URI` – your production MongoDB connection string
   - `CORS_ORIGINS` – your frontend URL(s), comma-separated (e.g. `https://app.example.com`)

2. **Never commit** `.env` – it contains secrets. Use `.env.example` as a template.

3. **Frontend**: Set `VITE_API_URL` when building if the backend is on a different domain.

4. **Rotate API keys** (GEMINI_API_KEY, SERPER_API_KEY) if they were ever exposed.

## Notes

- This is a standalone scraper project (no n8n integration)
- All data is stored in MongoDB
- The scraper uses Playwright for browser automation
- Respects rate limits and includes delays to avoid detection

## License

MIT
