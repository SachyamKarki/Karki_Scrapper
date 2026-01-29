import csv
import pymongo

import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

MONGO_URI = config.MONGO_URI
MONGO_DATABASE = config.MONGO_DATABASE
MONGO_COLLECTION = 'places' # logic assumes this name, or we can add to config if needed

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else 'data/bing_results_with_emails.csv'

def update_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[MONGO_COLLECTION]
    
    print(f"Reading {CSV_FILE}...")
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            updated_count = 0
            
            for row in reader:
                name = (row.get('name') or '').strip().strip('"')
                address = (row.get('address') or '').strip().strip('"')
                email = (row.get('email') or '').strip().strip('"')
                
                if name and email:
                    # Match by name, or name+address for reliability (handles duplicate names)
                    filter_query = {'name': name}
                    if address:
                        filter_query['address'] = address
                    result = collection.update_one(
                        filter_query,
                        {'$set': {'email': email}}
                    )
                    if result.modified_count > 0:
                        updated_count += 1
                        
            print(f"Successfully updated {updated_count} records with emails in MongoDB.")
            
    except Exception as e:
        print(f"Error: {e}")
        
    client.close()

if __name__ == "__main__":
    update_mongo()
