import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
import config

try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DATABASE]
    collection = db['users']

    count = collection.count_documents({})
    print(f"Total documents in 'users': {count}")

    if count > 0:
        print("\nAll users:")
        for doc in collection.find():
            print(f"Email: {doc.get('email')}, Role: {doc.get('role')}")
            print("-" * 20)
    else:
        print("No users found in database.")
except Exception as e:
    print(f"Error: {e}")
