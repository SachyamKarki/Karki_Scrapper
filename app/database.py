import pymongo

from config import MONGO_URI, MONGO_DATABASE

# MONGO_URI and MONGO_DATABASE are now loaded from config.py which reads from .env
# MONGO_URI = 'mongodb://localhost:27017/'
# MONGO_DATABASE = 'google_maps'
MONGO_COLLECTION = 'places'

def get_db_connection():
    # Use a new client per connection to avoid thread issues, 
    # or use a persistent client if properly managed. 
    # For this scale, creating a client is fine or using a global if managed by Flask g.
    client = pymongo.MongoClient(MONGO_URI)
    return client[MONGO_DATABASE][MONGO_COLLECTION]
