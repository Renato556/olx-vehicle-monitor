"""
Storage module for tracking seen listing IDs
Uses JSON file for persistence
"""

import json
import logging
import os
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

# File path for storing seen IDs (HAOS data volume)
DATA_FILE = "/data/seen_listings.json"

# Thread lock for file operations
_lock = Lock()


def load_seen_ids():
    """
    Load set of previously seen listing IDs from storage
    
    Returns:
        set: Set of listing ID strings
    """
    with _lock:
        if not os.path.exists(DATA_FILE):
            logger.info("No existing data file, starting fresh")
            return set()
        
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            seen_ids = set(data.get('seen_ids', []))
            last_update = data.get('last_update', 'unknown')
            
            logger.info(f"Loaded {len(seen_ids)} seen IDs (last update: {last_update})")
            return seen_ids
            
        except Exception as e:
            logger.error(f"Error loading seen IDs: {e}")
            # Return empty set on error to avoid crashes
            return set()


def save_seen_ids(new_ids):
    """
    Add new listing IDs to storage
    
    Args:
        new_ids: List or set of new listing ID strings to save
    """
    with _lock:
        # Load existing IDs
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                seen_ids = set(data.get('seen_ids', []))
            except Exception as e:
                logger.warning(f"Error loading existing IDs: {e}, starting fresh")
                seen_ids = set()
        else:
            seen_ids = set()
        
        # Add new IDs
        seen_ids.update(new_ids)
        
        # Prepare data for saving
        data = {
            'seen_ids': sorted(list(seen_ids)),  # Sort for cleaner diff
            'last_update': datetime.now().isoformat(),
            'total_count': len(seen_ids)
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # Write to file
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(new_ids)} new IDs (total: {len(seen_ids)})")
            
        except Exception as e:
            logger.error(f"Error saving seen IDs: {e}")
            raise
