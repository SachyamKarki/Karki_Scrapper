import certifi
import pymongo

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'google_maps'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'places')
        )

    def open_spider(self, spider):
        # tlsCAFile needed for MongoDB Atlas (mongodb+srv://)
        self.client = pymongo.MongoClient(
            self.mongo_uri,
            tlsCAFile=certifi.where()
        )
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # We want "fresh" results to appear at the top of the dashboard.
        # Since the dashboard sorts by _id (timestamp), we need a new _id for re-scraped items.
        # Strategy: Delete existing -> Insert as new.

        filter_query = {'name': item.get('name')}
        if item.get('address'):
             filter_query['address'] = item.get('address')
        
        # 1. Start clean (delete if exists)
        self.db[self.mongo_collection].delete_one(filter_query)
        
        # 2. Insert as new (gets new _id)
        self.db[self.mongo_collection].insert_one(dict(item))
        
        return item
