"""
Notification module for sending alerts via ntfy.sh
"""

import logging
import requests
import unicodedata
import time

logger = logging.getLogger(__name__)

# ntfy.sh has a 4096 byte limit for messages
# Keep messages under 3800 bytes for safety margin
MAX_MESSAGE_BYTES = 3800


def remove_accents(text):
    """
    Remove accents from text and characters that might break Markdown links
    
    Args:
        text: String with accents
        
    Returns:
        String without accents and problematic characters
    """
    if not text:
        return text
    
    # Normalize to NFD (decomposed form) and filter out combining marks
    nfd = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    # Remove characters that can break Markdown [text](url) structure
    # like [ and ] inside the title itself
    text = text.replace('[', '(').replace(']', ')')
    
    # Replace ( and ) with spaces as they also break some Markdown parsers when inside the label
    text = text.replace('(', ' ').replace(')', ' ')
    
    # Clean up double spaces
    text = ' '.join(text.split())
    
    return text


def format_listing(i, listing):
    """
    Format a single listing into a string block
    """
    # Remove accents and problematic chars from title
    clean_title = remove_accents(listing['title'])
    
    # Ensure URL is clean (no spaces or weird chars that might have survived)
    clean_url = listing['url'].replace(' ', '%20')
    
    # Create hyperlink using Markdown format: [text](url)
    title_link = f"[{clean_title}]({clean_url})"
    
    lines = []
    lines.append(f"{i}. {title_link}")
    lines.append(f"   {listing['price']}")
    
    # Add location if available
    if listing.get('location'):
        location_no_accents = remove_accents(listing['location'])
        lines.append(f"   {location_no_accents}")
    
    lines.append("")  # Blank line between listings
    return "\n".join(lines)


def send_notification(listings, topic):
    """
    Send notification of new listings to ntfy.sh
    Splits into multiple messages based on byte size to avoid attachment files
    
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
    batches = []
    current_batch = []
    current_batch_size = 0
    
    for i, listing in enumerate(listings, 1):
        listing_text = format_listing(i, listing)
        listing_size = len(listing_text.encode('utf-8'))
        
        # If adding this listing exceeds the limit, start a new batch
        # We account for the header size roughly here (around 200 bytes)
        if current_batch_size + listing_size > MAX_MESSAGE_BYTES - 200:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_batch_size = 0
        
        current_batch.append(listing_text)
        current_batch_size += listing_size
    
    if current_batch:
        batches.append(current_batch)
    
    total_batches = len(batches)
    logger.info(f"Sending {total_listings} listings in {total_batches} message(s) to {topic}")
    
    try:
        for batch_num, batch_content in enumerate(batches, 1):
            if total_batches > 1:
                header = f"Novos Anuncios OLX - Parte {batch_num}/{total_batches} ({total_listings} total)\n\n"
                title = f"Novos Veiculos OLX ({batch_num}/{total_batches})"
            else:
                header = f"Novos Anuncios OLX - {total_listings} veiculo{'s' if total_listings != 1 else ''}\n\n"
                title = "Novos Veiculos OLX"
            
            message = header + "".join(batch_content)
            
            # Send to ntfy.sh
            ntfy_url = f"https://ntfy.sh/{topic}"
            
            logger.info(f"Sending batch {batch_num}/{total_batches} ({len(message.encode('utf-8'))} bytes)")
            
            headers = {
                "Title": remove_accents(title),
                "Tags": "car,olx",
                "Priority": "default",
                "X-Markdown": "yes"  # Using X-Markdown for maximum compatibility
            }
            
            response = requests.post(
                ntfy_url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Delay to avoid rate limiting or ordering issues
            if batch_num < total_batches:
                time.sleep(1.5)
                
        logger.info(f"All {total_batches} notification(s) sent successfully")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception(f"Failed to send notification to ntfy.sh: {e}")
