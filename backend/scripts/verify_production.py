import os
import sys
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def verify_production():
    print("Verifying Production Readiness...")
    print("-" * 30)

    # 1. Check Flask Debug Mode
    flask_debug = os.getenv('FLASK_DEBUG')
    print(f"[*] Checking FLASK_DEBUG: {flask_debug}")
    if flask_debug and flask_debug.lower() in ('true', '1', 't'):
        print("    [!] WARNING: FLASK_DEBUG is enabled. Ensure this is intentional for production.")
    else:
        print("    [OK] FLASK_DEBUG is disabled or unset (defaulting to False).")

    # 2. Check Database Connection
    print("\n[*] Checking MongoDB Connection...")
    print(f"    URI: {config.MONGO_URI.split('@')[-1] if '@' in config.MONGO_URI else 'localhost'}") # Mask credentials
    
    try:
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("    [OK] Connected to MongoDB successfully!")
    except Exception as e:
        print(f"    [FAIL] Could not connect to MongoDB: {e}")
        return False

    # 3. Check for Debug Files
    print("\n[*] Checking for temporary debug files...")
    debug_file = "debug_failed_scrape.html"
    if os.path.exists(debug_file):
        print(f"    [FAIL] Found {debug_file}. It should be removed.")
        return False
    else:
        print(f"    [OK] {debug_file} not found.")

    print("-" * 30)
    print("Verification Complete.")
    return True

if __name__ == "__main__":
    success = verify_production()
    if not success:
        sys.exit(1)
