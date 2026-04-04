"""
Notification module for sending alerts via ntfy.sh
"""

import logging
import requests
import unicodedata

logger = logging.getLogger(__name__)


def remove_accents(text):
    """
    Remove accents from text
    
    Args:
        text: String with accents
        
    Returns:
        String without accents
    """
    if not text:
        return text
    
    # Normalize to NFD (decomposed form) and filter out combining marks
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


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
    
    # Format message with all listings using Markdown format
    # ntfy.sh supports Markdown including hyperlinks
    message_lines = [
        f"Novos Anuncios OLX - {len(listings)} veiculo{'s' if len(listings) != 1 else ''}",
        ""
    ]
    
    for i, listing in enumerate(listings, 1):
        # Create hyperlink using Markdown format: [text](url)
        title_link = f"[{listing['title']}]({listing['url']})"
        
        message_lines.append(f"{i}. {title_link}")
        message_lines.append(f"   {listing['price']}")
        
        # Add location if available
        if listing.get('location'):
            location_no_accents = remove_accents(listing['location'])
            message_lines.append(f"   {location_no_accents}")
        
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
                "Title": "Novos Veiculos OLX",
                "Tags": "car,olx",
                "Priority": "default",
                "Markdown": "yes"  # Enable Markdown formatting
            },
            timeout=30
        )
        
        response.raise_for_status()
        logger.info(f"Notification sent successfully")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception(f"Failed to send notification to ntfy.sh: {e}")
