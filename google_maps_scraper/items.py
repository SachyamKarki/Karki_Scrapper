import scrapy

class GoogleMapsScraperItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    category = scrapy.Field() # <--- Added this
    batch_id = scrapy.Field()
    url = scrapy.Field()
