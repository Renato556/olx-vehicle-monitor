"""
OLX scraper module using curl-cffi for impersonation
Extracts vehicle listings from OLX Brazil
"""

import json
import logging
import re
import time
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def make_scraper():
    """Create session with real Chrome impersonation (genuine TLS fingerprint)."""
    session = cffi_requests.Session(impersonate="chrome120")
    session.headers.update(
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.olx.com.br/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    return session

def fetch_olx_listings(url):
    """
    Fetch vehicle listings from OLX using curl-cffi
    
    Args:
        url: OLX search URL with filters
        
    Returns:
        list: List of dicts with keys: id, title, price, url, location
    """
    scraper = make_scraper()
    try:
        logger.info(f"Fetching URL: {url[:80]}...")
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
        
        html = resp.text
        logger.info(f"Page loaded ({len(html)} bytes), extracting listings...")
        
        # Try extracting from __NEXT_DATA__ JSON first (more reliable)
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
            html,
            re.DOTALL
        )
        
        if match:
            try:
                data = json.loads(match.group(1))
                listings_data = data['props']['pageProps']['ads']
                
                listings = []
                for ad in listings_data:
                    # Extract mileage from properties if available
                    mileage = ""
                    properties = ad.get('properties', [])
                    for prop in properties:
                        if prop.get('name') == 'mileage':
                            mileage = prop.get('value', '')
                            break
                    
                    listing = {
                        'id': str(ad.get('listId', '')),
                        'title': ad.get('title', ad.get('subject', '')),
                        'price': ad.get('price', ''),
                        'mileage': mileage,
                        'url': ad.get('url', ''),
                        'location': ad.get('location', '')
                    }
                    if listing['id'] and listing['title'] and listing['url']:
                        listings.append(listing)
                
                if listings:
                    logger.info(f"Successfully extracted {len(listings)} listings via __NEXT_DATA__")
                    return listings
            except Exception as e:
                logger.warning(f"Failed to parse __NEXT_DATA__: {e}. Falling back to HTML parsing.")

        # Fallback to BeautifulSoup parsing
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        # Find listings in HTML (selectors based on OLX structure)
        cards = soup.select("section[data-ds-component='DS-AdCard']")
        if not cards:
            cards = soup.select("li[data-lurker-detail='list_id']")

        for card in cards:
            try:
                link_tag = card.find("a", href=True)
                if not link_tag: continue
                
                ad_url = link_tag["href"]
                title_tag = card.find(["h2", "h3"])
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                price_tag = card.find(string=re.compile(r"R\$\s*[\d\.,]+"))
                price = price_tag.strip() if price_tag else ""
                
                # Extract ID from URL
                id_match = re.search(r"-(\d{7,})(?:\.html)?$", ad_url)
                ad_id = id_match.group(1) if id_match else ad_url
                
                if ad_id and title:
                    listings.append({
                        'id': ad_id,
                        'title': title,
                        'price': price,
                        'url': ad_url,
                        'location': "" # Location extraction is secondary
                    })
            except Exception:
                continue

        logger.info(f"Successfully extracted {len(listings)} listings via HTML")
        return listings
            
    except Exception as e:
        logger.error(f"Error fetching listings: {e}")
        raise
