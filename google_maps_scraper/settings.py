BOT_NAME = 'google_maps_scraper'

SPIDER_MODULES = ['google_maps_scraper.spiders']
NEWSPIDER_MODULE = 'google_maps_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'google_maps')

ITEM_PIPELINES = {
    'google_maps_scraper.pipelines.MongoDBPipeline': 300,
}

# Playwright Settings
# Default to True for production safety, override in .env if needed
IS_HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": IS_HEADLESS,
    "timeout": 120000,
    "args": [
        "--incognito",
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-infobars",
        "--disable-extensions",
        "--disable-gpu",
        "--disable-setuid-sandbox",
        "--no-first-run",
    ],
    "ignore_default_args": ["--enable-automation"],
}

# Add delay to be more human-like
DOWNLOAD_DELAY = 3

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# MongoDB Collection
MONGO_COLLECTION = 'places'

