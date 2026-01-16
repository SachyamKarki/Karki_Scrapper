from pymongo import MongoClient
import pprint

client = MongoClient('mongodb://localhost:27017/')
db = client['google_maps']
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
