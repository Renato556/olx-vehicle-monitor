#!/usr/bin/env python3
"""Quick test of the monitor without running full loop"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Override DATA_FILE for local testing
import storage
storage.DATA_FILE = "/tmp/olx_test_data.json"

from scraper import fetch_olx_listings
from notifier import send_notification
from storage import load_seen_ids, save_seen_ids

OLX_URL = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg?ps=19000&pe=26000&sf=1&gb=1&gb=2&ics=1&ics=2&ics=5&hgnv=0&cf=1&fncs=1"
NTFY_TOPIC = "carros-mg-olx"

print("=" * 80)
print("OLX Monitor - Quick Test")
print("=" * 80)

# Test 1: Fetch listings
print("\n[1/4] Testing scraper...")
try:
    listings = fetch_olx_listings(OLX_URL)
    print(f"✓ Scraper works! Found {len(listings)} listings")
    print(f"  Sample: {listings[0]['title'][:50]}... - {listings[0]['price']}")
except Exception as e:
    print(f"✗ Scraper failed: {e}")
    sys.exit(1)

# Test 2: Storage
print("\n[2/4] Testing storage...")
try:
    seen = load_seen_ids()
    print(f"✓ Load works! Previously seen: {len(seen)} IDs")
    
    # Save first 3 IDs
    test_ids = [listings[0]['id'], listings[1]['id'], listings[2]['id']]
    save_seen_ids(test_ids)
    print(f"✓ Save works! Saved {len(test_ids)} test IDs")
    
    # Verify
    seen = load_seen_ids()
    print(f"✓ Verify works! Now have {len(seen)} total IDs")
except Exception as e:
    print(f"✗ Storage failed: {e}")
    sys.exit(1)

# Test 3: Find new listings
print("\n[3/4] Testing deduplication...")
try:
    seen_ids = load_seen_ids()
    new_listings = [l for l in listings if l['id'] not in seen_ids]
    print(f"✓ Deduplication works!")
    print(f"  Total: {len(listings)} | Seen: {len(seen_ids)} | New: {len(new_listings)}")
except Exception as e:
    print(f"✗ Deduplication failed: {e}")
    sys.exit(1)

# Test 4: Send notification (only if there are new listings)
print("\n[4/4] Testing notifier...")
if new_listings:
    print(f"  Sending test notification with {min(2, len(new_listings))} listing(s)...")
    try:
        # Send only first 2 to avoid spam
        send_notification(new_listings[:2], NTFY_TOPIC)
        print(f"✓ Notifier works! Message sent to ntfy.sh/{NTFY_TOPIC}")
        print(f"  Check your ntfy.sh app or visit: https://ntfy.sh/{NTFY_TOPIC}")
    except Exception as e:
        print(f"✗ Notifier failed: {e}")
        sys.exit(1)
else:
    print(f"  Skipping notification (no new listings to test with)")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nThe monitor is ready to deploy to HAOS.")
print(f"Test data stored in: {storage.DATA_FILE}")
print(f"\nTo clean up: rm {storage.DATA_FILE}")
