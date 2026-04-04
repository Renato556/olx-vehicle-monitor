"""
Notification module for sending alerts via ntfy.sh
"""

import logging
import requests

logger = logging.getLogger(__name__)


def send_notification(listings, topic):
    """
    Send notification of new listings to ntfy.sh
    
    Args:
        listings: List of listing dicts with keys: id, title, price, url, location
        topic: ntfy.sh topic name (e.g. "carros-mg-olx")
    
    Raises:
        Exception: If notification fails to send
    """
    if not listings:
        logger.warning("No listings to notify")
        return
    
    # Format message with all listings
    message_lines = [
        f"🚗 Novos Anúncios OLX - {len(listings)} veículo{'s' if len(listings) != 1 else ''}",
        ""
    ]
    
    for i, listing in enumerate(listings, 1):
        message_lines.append(f"{i}. {listing['title']}")
        message_lines.append(f"   {listing['price']}")
        message_lines.append(f"   {listing['url']}")
        
        # Add location if available
        if listing.get('location'):
            message_lines.append(f"   📍 {listing['location']}")
        
        message_lines.append("")  # Blank line between listings
    
    message = "\n".join(message_lines)
    
    # Send to ntfy.sh
    ntfy_url = f"https://ntfy.sh/{topic}"
    
    try:
        logger.info(f"Sending notification with {len(listings)} listings to {topic}")
        
        response = requests.post(
            ntfy_url,
            data=message.encode('utf-8'),
            headers={
                "Title": f"Novos Veículos OLX ({len(listings)})",
                "Tags": "car,olx",
                "Priority": "default"
            },
            timeout=30
        )
        
        response.raise_for_status()
        logger.info(f"Notification sent successfully")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception(f"Failed to send notification to ntfy.sh: {e}")
