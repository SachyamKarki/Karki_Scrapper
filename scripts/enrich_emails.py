import csv
import re
import asyncio
from playwright.async_api import async_playwright
import sys

INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "data/bing_results_json.csv"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "data/bing_results_with_emails.csv"

# Regex for email
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def fetch_emails(context, url):
    if not url or "http" not in url:
        return ""
    
    try:
        # Create a new page for each request to avoid pollution/stalls
        page = await context.new_page()
        print(f"Checking: {url}")
        
        # Fast timeout - if site is slow, skip it
        await page.goto(url, timeout=10000, wait_until="domcontentloaded")
        
        content = await page.content()
        emails = set(re.findall(EMAIL_REGEX, content))
        
        # Filter junk emails (images, extensions)
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.js', '.css'))]
        
        await page.close()
        
        if valid_emails:
            found = ", ".join(valid_emails)
            print(f"  -> Found: {found}")
            return found
            
    except Exception as e:
        print(f"  -> Failed: {e}")
        try:
            await page.close()
        except: pass
        
    return ""

async def main():
    rows = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Loaded {len(rows)} items. Starting email scan...")


    # Load env for Headless config
    from dotenv import load_dotenv
    import os
    load_dotenv()
    is_headless = os.getenv('HEADLESS', 'True').lower() == 'true'

    async with async_playwright() as p:
        # Launch browser once
        browser = await p.chromium.launch(headless=is_headless)
        context = await browser.new_context(
             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Semaphore to limit concurrency
        sem = asyncio.Semaphore(5) 

        async def process_row(row):
            async with sem:
                website = row.get('website', '')
                if website:
                    email = await fetch_emails(context, website)
                    row['email'] = email
                else:
                    row['email'] = ""
                return row

        # Process all tasks
        tasks = [process_row(row) for row in rows]
        enriched_rows = await asyncio.gather(*tasks)
        
        await browser.close()
        
    # Write output
    if not rows:
        print("No data found in input CSV.")
        return

    fieldnames = list(rows[0].keys())
    if 'email' not in fieldnames:
        fieldnames.append('email')
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
