import scrapy

class GoogleMapsScraperItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    email = scrapy.Field()
    social_links = scrapy.Field()  # JSON: {"facebook": "url", "instagram": "url", ...}
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    category = scrapy.Field()
    batch_id = scrapy.Field()
    url = scrapy.Field()
