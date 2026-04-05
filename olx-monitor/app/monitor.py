#!/usr/bin/env python3
"""
OLX Vehicle Monitor - Main Application
Monitors OLX for new vehicle listings and sends notifications via ntfy.sh
"""

import logging
import sys
import time
from datetime import datetime

from scraper import fetch_olx_listings
from storage import load_seen_ids, save_seen_ids
from notifier import send_notification

# Configuration (hardcoded as per requirements)
OLX_URLS = [
    "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg/belo-horizonte-e-regiao?ps=19000&pe=26000&sf=1&f=p&gb=1&gb=2&ics=1&ics=2&ics=5&hgnv=0&cf=1&fncs=1",
    "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg/regiao-de-juiz-de-fora?ps=19000&pe=26000&sf=1&f=p&gb=1&gb=2&ics=1&ics=2&ics=5&hgnv=0&cf=1&fncs=1"
]
NTFY_TOPIC = "carros-olx-mg"
CHECK_INTERVAL = 600  # 10 minutes in seconds

# Keywords to ignore (case insensitive)
IGNORED_BRANDS = ["peugeot", "citroen", "citroën"]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main monitoring loop"""
    logger.info("=" * 80)
    logger.info("OLX Vehicle Monitor Starting")
    logger.info("=" * 80)
    logger.info(f"Monitoring {len(OLX_URLS)} URLs")
    logger.info(f"ntfy.sh topic: {NTFY_TOPIC}")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL/60:.0f} minutes)")
    logger.info("=" * 80)
    
    while True:
        try:
            check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"\n--- Check started at {check_time} ---")
            
            # Fetch current listings from all OLX URLs
            logger.info("Fetching listings from OLX...")
            all_fetched_listings = []
            for url in OLX_URLS:
                try:
                    listings = fetch_olx_listings(url)
                    all_fetched_listings.extend(listings)
                    # Small delay between requests to be polite
                    if len(OLX_URLS) > 1:
                        time.sleep(2)
                except Exception as e:
                    logger.error(f"Error fetching from {url[:50]}...: {e}")
            
            # Deduplicate listings by ID (in case a car appears in multiple search regions)
            unique_listings = {}
            for l in all_fetched_listings:
                unique_listings[l['id']] = l
            
            listings = list(unique_listings.values())
            logger.info(f"Fetched {len(listings)} unique listings total")
            
            # Load previously seen listing IDs
            seen_ids = load_seen_ids()
            logger.info(f"Previously seen: {len(seen_ids)} listings")
            
            # Filter to only new listings
            new_listings = [l for l in listings if l['id'] not in seen_ids]
            
            # Filter out ignored brands
            if new_listings:
                original_count = len(new_listings)
                new_listings = [
                    l for l in new_listings 
                    if not any(brand in l['title'].lower() for brand in IGNORED_BRANDS)
                ]
                filtered_count = original_count - len(new_listings)
                if filtered_count > 0:
                    logger.info(f"Filtered out {filtered_count} listings from ignored brands.")
            
            if new_listings:
                logger.info(f"Found {len(new_listings)} NEW listings!")
                
                # Log new listing details
                for i, listing in enumerate(new_listings, 1):
                    logger.info(f"  {i}. [{listing['id']}] {listing['title'][:50]}... - {listing['price']}")
                
                # Send notification with all new listings in one message
                try:
                    send_notification(new_listings, NTFY_TOPIC)
                    logger.info("Notification sent successfully")
                except Exception as e:
                    # Log error but continue (as per requirements: do nothing on error)
                    logger.error(f"Failed to send notification: {e}")
                
                # Save new listing IDs to storage
                try:
                    new_ids = [l['id'] for l in new_listings]
                    save_seen_ids(new_ids)
                    logger.info(f"Saved {len(new_ids)} new IDs to storage")
                except Exception as e:
                    # Log error but continue
                    logger.error(f"Failed to save IDs: {e}")
                    
            else:
                logger.info("No new listings found")
            
            logger.info(f"Check completed. Sleeping for {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
            sys.exit(0)
            
        except Exception as e:
            # Log error and continue loop (as per requirements: do nothing on error)
            logger.error(f"Error during check: {e}", exc_info=True)
            logger.info(f"Continuing despite error. Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
