#!/bin/bash
# Usage: ./run.sh "Search Query" [Batch ID]
# Example: ./run.sh "Gyms in Kathmandu" batch-123

cd "$(dirname "$0")" || exit

# Activate venv when present (local dev); Render/production uses system Python
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

QUERY="${1:-restaurants in kathmandu}"
BATCH_ID="${2:-default_session}"
OUTPUT="results.csv" # Fixed temp output

echo "Starting scraper for: $QUERY (Batch ID: $BATCH_ID)"

# Run Scrapy (Switching to BING for reliability)
scrapy crawl bing -a query="$QUERY" -a batch_id="$BATCH_ID" -O "data/last_scrape_raw.csv"

echo "Scraping complete. Starting Email Enrichment..."

# Run Email Enrichment
python3 scripts/enrich_emails.py "data/last_scrape_raw.csv" "data/last_scrape_enriched.csv"

echo "Enrichment complete."

# Auto-Merge to Persistent Excel (Restored)
echo "Merging data to consolidated Excel..."
# Merge the ENRICHED file
python3 scripts/merge_to_excel.py "data/last_scrape_enriched.csv" "data/consolidated_data.xlsx"

# Also sync emails to Mongo so they show up in UI
python3 scripts/update_mongo_emails.py "data/last_scrape_enriched.csv"

# Upload to MongoDB is handled by Scrapy Pipeline automatically with batch_id.

echo "Data saved to 'data/consolidated_data.xlsx' and MongoDB with Batch ID: $BATCH_ID"
