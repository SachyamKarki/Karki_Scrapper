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

## Troubleshooting

### Database not connecting
- **Check MongoDB**: Run `cd backend && source venv/bin/activate && python scripts/check_mongo.py`
- **API check**: Visit `http://localhost:5555/api/db_check` (or your backend URL + `/api/db_check`) – returns `connected: true` if MongoDB works
- **MongoDB Atlas**: Ensure `MONGO_URI` in `backend/.env` is correct and Network Access allows your IP (or `0.0.0.0/0` for production)

### Scraping not working
- **Playwright browser**: Run `cd backend && source venv/bin/activate && playwright install chromium` (required!)
- **Map not opening**: To see the browser window when scraping locally, add `HEADLESS=False` to `backend/.env`
- **Quick setup**: Run `./backend/scripts/setup_local.sh` to install deps + Playwright
- **Logs**: Check the terminal where the Flask backend runs for scrape errors

### Map link not opening (address in Dashboard)
- The address links to Google Maps. Ensure pop-up blockers allow new tabs.
- If blocked, right-click the address → "Open link in new tab"

### Local setup (frontend + backend)
```bash
# Terminal 1 – backend
cd backend && source venv/bin/activate && python app.py

# Terminal 2 – frontend
cd frontend && npm run dev
```
- Frontend: http://localhost:5173
- Backend: http://localhost:5555
- Frontend proxies `/api`, `/auth`, etc. to the backend

## Notes

- This is a standalone scraper project (no n8n integration)
- All data is stored in MongoDB
- The scraper uses Playwright for browser automation
- Respects rate limits and includes delays to avoid detection

## License

MIT
