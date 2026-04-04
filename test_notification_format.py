#!/usr/bin/env python3
"""Test notification format with hyperlinks"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from notifier import send_notification

# Sample listings
test_listings = [
    {
        'id': '1234567',
        'title': 'Fiat Uno Vivace 1.0 Flex 2015',
        'price': 'R$ 25.000',
        'url': 'https://mg.olx.com.br/item/1234567',
        'location': 'Belo Horizonte, São Paulo - DDD 31'
    },
    {
        'id': '7654321',
        'title': 'VW Gol 1.6 Total Flex 2018',
        'price': 'R$ 22.500',
        'url': 'https://mg.olx.com.br/item/7654321',
        'location': 'Contagem - DDD 31'
    }
]

print("=" * 80)
print("Testing New Notification Format")
print("=" * 80)
print("\nSending test notification with:")
print("- Hyperlinks on title (Markdown format)")
print("- No accents in text")
print("\nSample format preview:")
print("-" * 80)

# Show what the message will look like
from notifier import remove_accents

message_lines = [
    f"Novos Anuncios OLX - {len(test_listings)} veiculos",
    ""
]

for i, listing in enumerate(test_listings, 1):
    title_link = f"[{listing['title']}]({listing['url']})"
    message_lines.append(f"{i}. {title_link}")
    message_lines.append(f"   {listing['price']}")
    if listing.get('location'):
        location_no_accents = remove_accents(listing['location'])
        message_lines.append(f"   {location_no_accents}")
    message_lines.append("")

print("\n".join(message_lines))
print("-" * 80)

print("\nSending to ntfy.sh/carros-mg-olx...")
try:
    send_notification(test_listings, "carros-mg-olx")
    print("\n✅ SUCCESS! Notification sent with hyperlinks!")
    print("\nCheck your notification at:")
    print("  https://ntfy.sh/carros-mg-olx")
    print("\nThe titles should be clickable links!")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
