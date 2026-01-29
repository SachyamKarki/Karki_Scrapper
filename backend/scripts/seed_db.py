import pandas as pd
import pymongo
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

# Config
MONGO_URI = config.MONGO_URI
MONGO_DATABASE = config.MONGO_DATABASE
MONGO_COLLECTION = 'places'
CSV_FILE = 'gyms.csv'

def seed_db():
    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} not found.")
        return

    # Read CSV
    try:
        df = pd.read_csv(CSV_FILE)
        # Sanitize
        df = df.fillna("")
        data = df.to_dict(orient='records')
        
        if not data:
            print("No data in CSV.")
            return

        # Connect to DB
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DATABASE]
        collection = db[MONGO_COLLECTION]
        
        print(f"Seeding {len(data)} items to MongoDB...")
        
        for item in data:
            # Upsert based on name
            collection.update_one(
                {'name': item.get('name')},
                {"$set": item},
                upsert=True
            )
            
        print("Seeding complete.")
        print(f"Total documents: {collection.count_documents({})}")
        client.close()
        
    except Exception as e:
        print(f"Error seeding DB: {e}")

if __name__ == "__main__":
    seed_db()
