import sys
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

email = "admin@karki.com"
new_password = "admin123"

try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DATABASE]
    collection = db['users']

    result = collection.update_one(
        {'email': email},
        {'$set': {'password_hash': generate_password_hash(new_password)}}
    )

    if result.matched_count == 0:
        print(f"User {email} not found.")
    else:
        print(f"Successfully reset password for {email} to {new_password}")
except Exception as e:
    print(f"Error: {e}")
