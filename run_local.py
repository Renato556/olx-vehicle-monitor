#!/usr/bin/env python3
"""
Run OLX monitor locally for testing
- Uses /tmp for data storage
- Runs only ONE check (no infinite loop)
- Shows detailed output
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Override DATA_FILE for local testing
import storage
storage.DATA_FILE = "/tmp/olx_monitor_data.json"

import logging
from datetime import datetime
from scraper import fetch_olx_listings
from notifier import send_notification
from storage import load_seen_ids, save_seen_ids

# Configuration
OLX_URL = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg?ps=19000&pe=26000&sf=1&gb=1&gb=2&ics=1&ics=2&ics=5&hgnv=0&cf=1&fncs=1"
NTFY_TOPIC = "carros-mg-olx"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("OLX VEHICLE MONITOR - LOCAL TEST RUN")
    logger.info("=" * 80)
    logger.info(f"Data file: {storage.DATA_FILE}")
    logger.info(f"ntfy.sh topic: {NTFY_TOPIC}")
    logger.info("=" * 80)
    
    try:
        check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\nCheck started at {check_time}")
        
        # Fetch current listings from OLX
        logger.info("Fetching listings from OLX...")
        listings = fetch_olx_listings(OLX_URL)
        logger.info(f"✓ Fetched {len(listings)} total listings")
        
        # Load previously seen listing IDs
        seen_ids = load_seen_ids()
        logger.info(f"✓ Previously seen: {len(seen_ids)} listings")
        
        # Filter to only new listings
        new_listings = [l for l in listings if l['id'] not in seen_ids]
        
        if new_listings:
            logger.info(f"\n🎉 Found {len(new_listings)} NEW listings!")
            logger.info("=" * 80)
            
            # Show details of new listings
            for i, listing in enumerate(new_listings[:10], 1):  # Show max 10
                logger.info(f"\n  {i}. [{listing['id']}] {listing['title'][:60]}")
                logger.info(f"     Price: {listing['price']}")
                logger.info(f"     Location: {listing.get('location', 'N/A')}")
                logger.info(f"     URL: {listing['url'][:70]}...")
            
            if len(new_listings) > 10:
                logger.info(f"\n  ... and {len(new_listings) - 10} more")
            
            # In non-interactive environment, we skip the prompt and send automatically
            # if the user specifically asked to run it.
            logger.info(f"\nSending notification with {len(new_listings)} listings to ntfy.sh/{NTFY_TOPIC}...")
            
            # Send notification with all new listings
            send_notification(new_listings, NTFY_TOPIC)
            logger.info("✓ Notification sent successfully!")
            logger.info(f"\nCheck at: https://ntfy.sh/{NTFY_TOPIC}")
            
            # Save new listing IDs
            new_ids = [l['id'] for l in new_listings]
            save_seen_ids(new_ids)
            logger.info(f"✓ Saved {len(new_ids)} new IDs to storage")
                
        else:
            logger.info("\nNo new listings found (all have been seen before)")
        
        logger.info("\n" + "=" * 80)
        logger.info("CHECK COMPLETED")
        logger.info("=" * 80)
        logger.info(f"\nData stored in: {storage.DATA_FILE}")
        logger.info(f"To reset: rm {storage.DATA_FILE}")
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Error during check: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
