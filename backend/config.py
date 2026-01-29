"""
Configuration file for Google Maps Scraper
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
load_dotenv(Path(__file__).resolve().parent.parent / '.env')
load_dotenv()  # cwd override

# Analysis Configuration
ANALYSIS_TIMEOUT = 10  # seconds for website to respond
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Database Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'google_maps')

# SECRET_KEY: Required in production. Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
_is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENV') == 'production'
_default_secret = os.getenv('SECRET_KEY')
if _is_production and (not _default_secret or _default_secret == 'dev-secret-key-change-in-production'):
    raise ValueError('SECRET_KEY must be set in production. Set it in .env')
SECRET_KEY = _default_secret or 'dev-secret-key-change-in-production'
