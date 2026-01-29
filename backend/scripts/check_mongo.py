import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
import pprint
import config

client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DATABASE]
collection = db['places']

count = collection.count_documents({})
print(f"Total documents in 'places': {count}")

if count > 0:
    print("\nLast 3 documents:")
    for doc in collection.find().sort('_id', -1).limit(3):
        print(f"Name: {doc.get('name')}")
        print(f"Address: {doc.get('address')}")
        print(f"Phone: {doc.get('phone')}")
        print(f"Rating: {doc.get('rating')}")
        print(f"Website: {doc.get('website')}")
        print("-" * 20)
