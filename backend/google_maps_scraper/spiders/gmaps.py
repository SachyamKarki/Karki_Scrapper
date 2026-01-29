import re
import scrapy
from scrapy_playwright.page import PageMethod
from google_maps_scraper.items import GoogleMapsScraperItem
import asyncio
from urllib.parse import parse_qs, urlparse
import os
import json

class GmapsSpider(scrapy.Spider):
    name = "gmaps"
    allowed_domains = ["google.com"]

    def __init__(self, query=None, batch_id=None, *args, **kwargs):
        super(GmapsSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.batch_id = batch_id
        # Rotation of User Agents
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
        ]

    def start_requests(self):
        if not self.query:
            self.query = "restaurants in kathmandu"
        
        url = f"https://www.google.com/maps/search/{self.query}?hl=en"
        
        # Load cookies if available
        cookies = []
        cookie_file = "cookies.json"
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r') as f:
                    cookies = json.load(f)
                    print(f"DEBUG: Loaded {len(cookies)} cookies from {cookie_file}")
            except Exception as e:
                print(f"DEBUG: Error loading cookies: {e}")
        else:
            print("DEBUG: No cookies.json found. Running unauthenticated.")

        import random
        ua = random.choice(self.user_agents)
        print(f"DEBUG: Using User-Agent: {ua}")
        
        context_args = {
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": ua,
            # Force empty storage to simulate incognito behavior strictly
            "storage_state": None,
        }
        
        if cookies:
            context_args["cookies"] = cookies

        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context_args": context_args,
                # Wait for the feed (list results) to ensure page is loaded
                # "playwright_page_methods": [
                #    PageMethod("wait_for_selector", "div[role='feed']"),
                # ],
            },
            # callback=self.parse
            callback=self.parse
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        # Random human delay
        import random
        await asyncio.sleep(random.uniform(2, 5))
        
        # Debug: Take screenshot to see what's loading
        await page.screenshot(path="debug_start.png")
        
        # Handle Consent Screen (Before you continue)
        try:
            # Check for common consent buttons
            if await page.locator("button[aria-label='Accept all']").count() > 0:
                print("DEBUG: Clicking 'Accept all' (aria-label)...")
                await page.locator("button[aria-label='Accept all']").click()
                await page.wait_for_load_state("networkidle")
            elif await page.get_by_text("Accept all").count() > 0:
                 print("DEBUG: Clicking 'Accept all' (text)...")
                 await page.get_by_text("Accept all").click()
                 await page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"DEBUG: Consent handling error (might not be present): {e}")

        # robust wait: wait for feed OR first result
        try:
            # Wait for either the feed or a result link to appear
            # Increased timeout to 120s to allow MANUAL CAPTCHA SOLVING by user
            print("DEBUG: Waiting 120s for user to solve Captcha/Content to load...")
            await page.wait_for_selector("div[role='feed'], a[href*='/maps/place/']", timeout=120000)
            print("DEBUG: Initial content loaded.")
        except:
            print(f"DEBUG: Timeout waiting for initial content. Page title: {await page.title()}")
            await page.screenshot(path="debug_timeout.png")
            
            # Dump HTML for debugging
            content = await page.content()
            with open("debug_failed.html", "w", encoding="utf-8") as f:
                f.write(content)
            
            # Continue anyway to see if we can find anything logic below might salvage it
        
        # 1. Identify the scrollable container
        # Google Maps results are usually in a div with role='feed' OR a specific aria-label
        feed_selector = "div[role='feed']"
        if await page.locator(feed_selector).count() == 0:
            # Try fallback: div with "Results" in aria-label?
            # Or just assume the sidebar is the active element if we hover/click?
            # Let's try to find a div that contains the results.
            print("DEBUG: div[role='feed'] not found. Looking for alternatives...")
            
            # Try finding a[href*='/maps/place/'] parent
            if await page.locator("a[href*='/maps/place/']").count() > 0:
                 print("DEBUG: Found result links, but not feed with role='feed'. Using body/window scroll fallback.")
                 feed_selector = None # Signal to use window scroll or keyboard
            pass

        # 2. Scroll to load Items
        # If we found the feed, scroll it.
        # If not, we might try scrolling the page or a generic sidebar selector.
        
        print("Starting scroll loop...")
        for _ in range(4): # Increased scroll count
            try:
                # Try standard feed scroll
                if feed_selector and await page.locator(feed_selector).count() > 0:
                    await page.evaluate(f"document.querySelector('{feed_selector}').scrollBy(0, 1000)")
                else:
                    # Fallback: find the side pane (often has role='main' or region?)
                    # Attempt to press 'End' key which often scrolls the active container
                    await page.keyboard.press("End")
                    await page.mouse.wheel(0, 1000)
                
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Scroll error: {e}")

        # DEBUG: Deep Inspection
        print(f"DEBUG: Current URL: {page.url}")
        print(f"DEBUG: Current Title: {await page.title()}")
        await page.screenshot(path="debug_final.png")
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
            
        # DEBUG: Inspect what links are actually found
        all_links = page.locator("a")
        count_all = await all_links.count()
        print(f"DEBUG: Total 'a' tags found: {count_all}")
        for i in range(min(count_all, 15)):
             print(f"DEBUG Link {i}: {await all_links.nth(i).get_attribute('href')}")
        
        # UPDATE: 'a.hfpxzc' is fragile. Use href pattern which is more robust.
        locators = page.locator("a[href*='/maps/place/']")
        count = await locators.count()
        
        print(f"Found {count} items to scrape...")

        for i in range(count):
            try:
                href = await locators.nth(i).get_attribute("href")
                # if href and "/maps/place/" in href:  # Redundant check if selector is good but safe
                if href:           
                     # Send a request to the detail page
                     yield scrapy.Request(
                        url=href,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            # Wait for the main header (H1) which is the Place Name
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "h1", timeout=10000),
                            ],
                        },
                        callback=self.parse_detail
                    )

            except Exception as e:
                print(f"Error extracting item {i}: {e}")
                
        await page.close()

    async def parse_detail(self, response):
        page = response.meta["playwright_page"]
        
        item = GoogleMapsScraperItem()
        # Add batch_id if present
        if self.batch_id:
            item['batch_id'] = self.batch_id
            
        # Extract Name (H1)
        item['name'] = await page.locator('h1').inner_text()
        
        try:
             # Address - using data-item-id="address"
             if await page.locator('button[data-item-id="address"]').count() > 0:
                 text = await page.locator('button[data-item-id="address"]').inner_text()
                 if text:
                    # Regex cleaning: remove "Address:" prefix then strip ANY leading non-alphanumeric chars (icons, punctuation)
                    text = text.replace("Address: ", "").replace("\n", ", ")
                    # Remove generic icon codes if present (just in case)
                    text = text.replace("\ue0c8", "") 
                    # Strip leading non-word characters (icons usually fall here as symbols)
                    item['address'] = re.sub(r'^[^\w\d]+', '', text).strip()
             
             # Phone - using data-item-id starting with "phone"
             if await page.locator('button[data-item-id^="phone"]').count() > 0:
                  text = await page.locator('button[data-item-id^="phone"]').inner_text()
                  if text:
                    text = text.replace("Phone: ", "").replace("\n", "")
                    text = text.replace("\ue0b0", "")
                    # Strip leading non-word characters
                    item['phone'] = re.sub(r'^[^\w\d]+', '', text).strip()

             # Website - using data-item-id="authority"
             # If URL is facebook/instagram/whatsapp etc, put in social_links NOT website
             SOCIAL_MAP = {
                 'facebook.com': 'facebook', 'fb.com': 'facebook', 'fb.me': 'facebook', 'm.facebook.com': 'facebook',
                 'instagram.com': 'instagram', 'ig.me': 'instagram',
                 'whatsapp.com': 'whatsapp', 'wa.me': 'whatsapp',
                 'twitter.com': 'twitter', 'x.com': 'twitter',
                 'linkedin.com': 'linkedin', 'youtube.com': 'youtube', 'youtu.be': 'youtube', 'tiktok.com': 'tiktok'
             }
             def is_social_url_gmaps(url):
                 if not url or not isinstance(url, str): return None
                 u = url.lower()
                 for domain, platform in SOCIAL_MAP.items():
                     if domain in u: return platform
                 return None

             if await page.locator('a[data-item-id="authority"]').count() > 0:
                 raw_url = await page.locator('a[data-item-id="authority"]').get_attribute("href")
                 if raw_url:
                     if "/url?q=" in raw_url:
                         try:
                             parsed = urlparse(raw_url)
                             qs = parse_qs(parsed.query)
                             raw_url = qs.get('q', [raw_url])[0]
                         except: pass
                     platform = is_social_url_gmaps(raw_url)
                     if platform:
                         social = json.loads(item.get('social_links') or '{}')
                         social[platform] = raw_url
                         item['social_links'] = json.dumps(social)
                         item['website'] = None
                     else:
                         item['website'] = raw_url
            
             # Email - mailto links or data-item-id containing email
             if await page.locator('a[href^="mailto:"]').count() > 0:
                 mailto = await page.locator('a[href^="mailto:"]').first.get_attribute("href")
                 if mailto:
                     email = mailto.replace("mailto:", "").split("?")[0].strip()
                     if email and "@" in email:
                         item['email'] = email
             if not item.get('email') and await page.locator('button[data-item-id*="email"], a[data-item-id*="email"]').count() > 0:
                 text = await page.locator('button[data-item-id*="email"], a[data-item-id*="email"]').first.inner_text()
                 if text and "@" in text:
                     item['email'] = re.sub(r'[^\w.@+-]', '', text)
            
             # Social links - a[href*="facebook"], instagram, whatsapp, etc.
             social = json.loads(item.get('social_links') or '{}')
             social_domains = [('facebook.com', 'facebook'), ('instagram.com', 'instagram'), ('whatsapp.com', 'whatsapp'), ('wa.me', 'whatsapp'), ('twitter.com', 'twitter'), ('x.com', 'twitter'), ('linkedin.com', 'linkedin'), ('youtube.com', 'youtube')]
             for domain, platform in social_domains:
                 links = page.locator(f'a[href*="{domain}"]')
                 if await links.count() > 0:
                     href = await links.first.get_attribute("href")
                     if href and platform not in social:
                         if "/url?q=" in href:
                             try:
                                 parsed = urlparse(href)
                                 qs = parse_qs(parsed.query)
                                 href = qs.get('q', [href])[0]
                             except: pass
                         social[platform] = href
             if social:
                 item['social_links'] = json.dumps(social)
            
             # Rating - Try multiple reliable selectors
             # 1. Try the aria-label on the stars container
             rating_found = False
             
             # DEBUG: Print html around stars to logs
             # if await page.locator('span[role="img"][aria-label*="stars"]').count() > 0:
             #    print(f"DEBUG HTML: {await page.locator('span[role=\"img\"][aria-label*=\"stars\"]').first.evaluate('el => el.outerHTML')}")

             if await page.locator('span[role="img"][aria-label*="stars"]').count() > 0:
                 text = await page.locator('span[role="img"][aria-label*="stars"]').get_attribute("aria-label")
                 if text:
                    # "4.5 stars" -> "4.5"
                    item['rating'] = text.split(" ")[0]
                    rating_found = True
             
             # 2. Fallback: Try the direct numeric span class .MW4etd
             # Ensure we get the text visible on screen
             if not rating_found:
                 if await page.locator('div.TIHn2').count() > 0: # Parent container often TIHn2 or F7nice
                     # Try to find any nested span with strict pattern X.X
                     rating_text = await page.locator('div.TIHn2').inner_text()
                     match = re.search(r'(\d\.\d)', rating_text)
                     if match:
                         item['rating'] = match.group(1)
                         rating_found = True

             if not rating_found:
                  # Last ditch: look for any span with text matching X.X near the top
                  try:
                      # We restrict to the font headline area or summary
                      # This is risky but effective if specific classes change
                      possible_ratings = await page.locator('span').filter(has_text=re.compile(r'^\d\.\d$')).all_text_contents()
                      if possible_ratings:
                          item['rating'] = possible_ratings[0]
                  except:
                      pass
             
             # Reviews Count - usually a button with aria-label containing "reviews"
             if await page.locator('button[aria-label*="reviews"]').count() > 0:
                 text = await page.locator('button[aria-label*="reviews"]').inner_text()
                 if text:
                    item['reviews_count'] = text.replace("(", "").replace(")", "").strip()
                 
        except Exception as e:
            print(f"Error parsing detail: {e}")
        
        await page.close()
        yield item
