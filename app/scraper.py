"""
OLX scraper module using Playwright
Extracts vehicle listings from OLX Brazil
"""

import json
import logging
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


def fetch_olx_listings(url):
    """
    Fetch vehicle listings from OLX
    
    Args:
        url: OLX search URL with filters
        
    Returns:
        list: List of dicts with keys: id, title, price, url, location
        
    Raises:
        Exception: If scraping fails
    """
    try:
        with sync_playwright() as p:
            logger.info("Starting Playwright browser...")
            browser = p.chromium.launch(headless=True)
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            logger.info(f"Fetching URL: {url[:80]}...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for JavaScript to populate __NEXT_DATA__
            time.sleep(5)
            
            # Get page HTML
            html = page.content()
            browser.close()
            
            logger.info(f"Page loaded ({len(html)} bytes), extracting listings...")
            
            # Extract __NEXT_DATA__ JSON embedded in page
            match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
                html,
                re.DOTALL
            )
            
            if not match:
                raise Exception("Could not find __NEXT_DATA__ in page HTML")
            
            data = json.loads(match.group(1))
            
            # Navigate to listings array in JSON structure
            try:
                listings_data = data['props']['pageProps']['ads']
            except KeyError as e:
                raise Exception(f"Unexpected JSON structure in __NEXT_DATA__: {e}")
            
            if not isinstance(listings_data, list):
                raise Exception("Expected ads to be a list")
            
            # Parse listings into clean format
            listings = []
            for ad in listings_data:
                listing = {
                    'id': str(ad.get('listId', '')),
                    'title': ad.get('title', ad.get('subject', '')),
                    'price': ad.get('price', ''),
                    'url': ad.get('url', ''),
                    'location': ad.get('location', '')
                }
                
                # Only add if has minimum required fields
                if listing['id'] and listing['title'] and listing['url']:
                    listings.append(listing)
            
            logger.info(f"Successfully extracted {len(listings)} listings")
            return listings
            
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout loading page: {e}")
        raise Exception(f"Timeout loading OLX page: {e}")
        
    except Exception as e:
        logger.error(f"Error fetching listings: {e}")
        raise
