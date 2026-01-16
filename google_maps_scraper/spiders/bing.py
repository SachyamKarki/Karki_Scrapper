import scrapy
from google_maps_scraper.items import GoogleMapsScraperItem
import asyncio

class BingSpider(scrapy.Spider):
    name = "bing"
    allowed_domains = ["bing.com"]
    
    def __init__(self, query=None, batch_id=None, *args, **kwargs):
        super(BingSpider, self).__init__(*args, **kwargs)
        self.query = query or "gyms in kathmandu"
        self.batch_id = batch_id

    def start_requests(self):
        url = f"https://www.bing.com/maps?q={self.query}"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context_args": {
                    "ignore_https_errors": True,
                    "viewport": {"width": 1920, "height": 1080},
                }
            },
            callback=self.parse
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        # Wait for results to load
        try:
            await page.wait_for_selector(".b_maglistcard", timeout=15000)
        except:
             print("DEBUG: Timeout waiting for Bing results.")
        
        # Extract items using Scrapy selector on the current page content
        content = await page.content()
        response = scrapy.http.HtmlResponse(url=page.url, body=content, encoding='utf-8')
        
        # Selectors based on inspection
        cards = response.css(".b_maglistcard")
        print(f"DEBUG: Found {len(cards)} cards (b_maglistcard)")
        
        if not cards:
            print("DEBUG: No list cards found. Attempting Single Result Fallback...")
            
            # --- Single Result / Sidebar Logic ---
            single_item = GoogleMapsScraperItem()
            single_item['batch_id'] = self.batch_id
            single_item['url'] = page.url
            
            # STRATEGY 1: Parse data-entity JSON (Broad Search)
            # Sometimes class names change (e.g. .local-magazine, .b_cnt), best to look for the attribute anywhere.
            data_entities = response.css('*[data-entity]::attr(data-entity)').getall()
            for raw_json in data_entities:
                try:
                    import json
                    data = json.loads(raw_json)
                    # Support both {entity: {...}} and the entity dict itself
                    entity = data.get('entity', data)
                    
                    # Check if this entity looks like what we want (has name/phone/website)
                    # Note: "entryName" or "primaryCategoryName" are good signals
                    if entity.get('website') or entity.get('phone') or entity.get('primaryCategoryName'):
                        print("DEBUG: Found Valid Entity JSON. Extracting...")
                        
                        # Only overwrite if not already set (or just set it, it's reliable)
                        if entity.get('phone'): single_item['phone'] = entity.get('phone')
                        if entity.get('website'): single_item['website'] = entity.get('website')
                        if entity.get('primaryCategoryName'): single_item['category'] = entity.get('primaryCategoryName')
                        
                        # If we found a website, we are likely done
                        if single_item.get('website'):
                            break
                            
                except json.JSONDecodeError:
                    continue

            # STRATEGY 2: Text Scrapers (Fallback / Gap Fill)
            # 1. Try Title
            # Bing often puts title in h2.b_entityTitle or .b_focusTextMedium
            # Use xpath string(.) to get text even if nested in span/a/div
            name = response.css('h2.b_entityTitle').xpath('string(.)').get() or \
                   response.css('.b_focusTextMedium').xpath('string(.)').get() or \
                   response.css('.name').xpath('string(.)').get() or \
                   response.css('div.title').xpath('string(.)').get()
            
            if name:
                print(f"DEBUG: Found Single Result Name: {name.strip()}")
                single_item['name'] = name.strip()
                
                # 2. Try Address (only if not already set?)
                # Often in .b_address or .address
                address = response.css('.b_address').xpath('string(.)').get() or \
                          response.css('.address').xpath('string(.)').get()
                if address:
                    single_item['address'] = address.strip()
                
                # 3. Try Phone (Fallback if JSON missed)
                if not single_item.get('phone'):
                     phone = response.css('a[href^="tel:"]').xpath('string(.)').get()
                     if phone:
                        single_item['phone'] = phone.strip()
                
                # 4. Try Website (Fallback if JSON missed)
                if not single_item.get('website'):
                    website = response.css('a.website::attr(href)').get() or \
                              response.xpath('//a[contains(text(), "Website")]/@href').get()
                    single_item['website'] = website
                
                yield single_item
            else:
                 print("DEBUG: Failed to extract even a single result.")
                 # Dump HTML only if TRULY failed
                 with open('debug_failed_scrape.html', 'w', encoding='utf-8') as f:
                     f.write(response.text)
            
            return
        
        import json

        for card in cards:
            item = GoogleMapsScraperItem()
            item['batch_id'] = self.batch_id
            item['url'] = page.url # Map URL
            
            # Extract JSON from data-entity attribute (JACKPOT!)
            data_entity_str = card.attrib.get('data-entity')
            if data_entity_str:
                try:
                    data = json.loads(data_entity_str)
                    entity = data.get('entity', {})
                    
                    item['name'] = entity.get('title')
                    item['address'] = entity.get('address')
                    item['phone'] = entity.get('phone')
                    item['website'] = entity.get('website')
                    item['category'] = entity.get('primaryCategoryName') # <--- Extracted category
                    
                    # Rating/Reviews might be in there too, or we fall back to CSS
                    # entity keys often: title, id, address, phone, website, etc.
                    
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for card: {card}")
            
            # If JSON missing or failed, fallbacks
            if not item.get('name'):
                item['name'] = card.css("h3.l_magTitle::text").get()
            
            # Rating/Reviews often NOT in the JSON entity, so we scrape them from UI
            # Rating: .cico span (aria-label="4.5 stars")
            rating_text = card.css(".cico span::attr(aria-label)").get() 
            if rating_text:
                 item['rating'] = rating_text.split(" ")[0]
            
            # Reviews count: .l_rev_rc span (title="4 reviews") or text
            reviews_text = card.css(".l_rev_rc span::text").get()
            if reviews_text:
                 # Clean "(4 reviews)" -> "4"
                 import re
                 match = re.search(r'\d+', reviews_text)
                 if match:
                     item['reviews_count'] = match.group(0)

            yield item

        await page.close()
