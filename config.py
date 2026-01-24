"""
Configuration file for Google Maps Scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Analysis Configuration
ANALYSIS_TIMEOUT = 10  # seconds for website to respond
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Database Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'google_maps')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# No API key needed! Analysis is done locally using web scraping
