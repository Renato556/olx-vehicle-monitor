"""
Notification module for sending alerts via ntfy.sh
"""

import logging
import requests
import unicodedata
import time

logger = logging.getLogger(__name__)

# Maximum listings per message to avoid creating attachment files
# ntfy.sh creates attachments when message is too large
MAX_LISTINGS_PER_MESSAGE = 10


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


def send_single_message(listings_batch, batch_num, total_batches, total_listings, topic):
    """
    Send a single notification message
    
    Args:
        listings_batch: List of listings for this batch
        batch_num: Current batch number (1-indexed)
        total_batches: Total number of batches
        total_listings: Total number of listings across all batches
        topic: ntfy.sh topic name
    
    Raises:
        Exception: If notification fails to send
    """
    # Format message with listings using Markdown format
    message_lines = []
    
    # Header with batch info if multiple batches
    if total_batches > 1:
        message_lines.append(
            f"Novos Anuncios OLX - Parte {batch_num}/{total_batches} ({total_listings} total)"
        )
    else:
        message_lines.append(
            f"Novos Anuncios OLX - {total_listings} veiculo{'s' if total_listings != 1 else ''}"
        )
    
    message_lines.append("")
    
    # Calculate starting index for this batch
    start_idx = (batch_num - 1) * MAX_LISTINGS_PER_MESSAGE + 1
    
    for i, listing in enumerate(listings_batch, start=start_idx):
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
    
    # Title varies based on batch
    if total_batches > 1:
        title = f"Novos Veiculos OLX ({batch_num}/{total_batches})"
    else:
        title = "Novos Veiculos OLX"
    
    response = requests.post(
        ntfy_url,
        data=message.encode('utf-8'),
        headers={
            "Title": title,
            "Tags": "car,olx",
            "Priority": "default",
            "Markdown": "yes"  # Enable Markdown formatting
        },
        timeout=30
    )
    
    response.raise_for_status()


def send_notification(listings, topic):
    """
    Send notification of new listings to ntfy.sh
    Splits into multiple messages if needed to avoid attachment files
    
    Args:
        listings: List of listing dicts with keys: id, title, price, url, location
        topic: ntfy.sh topic name (e.g. "carros-mg-olx")
    
    Raises:
        Exception: If notification fails to send
    """
    if not listings:
        logger.warning("No listings to notify")
        return
    
    total_listings = len(listings)
    
    # Calculate number of batches needed
    total_batches = (total_listings + MAX_LISTINGS_PER_MESSAGE - 1) // MAX_LISTINGS_PER_MESSAGE
    
    logger.info(
        f"Sending {total_listings} listings in {total_batches} message(s) to {topic}"
    )
    
    try:
        # Split listings into batches and send
        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * MAX_LISTINGS_PER_MESSAGE
            end_idx = min(start_idx + MAX_LISTINGS_PER_MESSAGE, total_listings)
            
            batch = listings[start_idx:end_idx]
            
            logger.info(
                f"Sending batch {batch_num}/{total_batches} ({len(batch)} listings)"
            )
            
            send_single_message(batch, batch_num, total_batches, total_listings, topic)
            
            # Small delay between messages to avoid rate limiting
            if batch_num < total_batches:
                time.sleep(1)
        
        logger.info(f"All {total_batches} notification(s) sent successfully")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception(f"Failed to send notification to ntfy.sh: {e}")
