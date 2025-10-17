"""
Ownership Calculator - Retrieves partner ownership data
KISS principle: Does one thing - fetch ownership data with caching
"""
from typing import List, Dict, Any
import asyncio
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import config
from shared.firestore_client import firestore_client
from shared.logger import logger


class OwnershipCalculator:
    """
    Retrieves and caches partner ownership data

    Single Responsibility: Ownership data retrieval only
    """

    def __init__(self, cache):
        """
        Initialize ownership calculator

        Args:
            cache: Cache instance for ownership data
        """
        self.cache = cache

    async def get_ownership(self, terminal: str) -> List[Dict[str, Any]]:
        """
        Get partner ownership data for a terminal (with caching)

        Args:
            terminal: Terminal name

        Returns:
            List of partner ownership records with percentages

        Raises:
            ValueError: If no ownership data found
        """
        cache_key = f"ownership_{terminal}"

        # Try cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for terminal ownership: {terminal}")
            return cached_data

        # Cache miss - query Firestore
        logger.debug(f"Cache miss for terminal ownership: {terminal}, querying Firestore")

        try:
            ownership_data = await asyncio.to_thread(
                firestore_client.query_documents,
                collection=config.COLLECTION_PARTNER_OWNERSHIP,
                filters=[
                    ('terminal', '==', terminal),
                    ('active', '==', True)
                ]
            )

            if not ownership_data:
                logger.warning(f"No ownership data found for terminal: {terminal}")
                raise ValueError(f"No ownership data found for terminal: {terminal}")

            # Validate ownership percentages sum to 100%
            total_percentage = sum(o.get('ownership_percentage', 0) for o in ownership_data)
            if abs(total_percentage - 100.0) > 0.01:  # Allow small floating point errors
                logger.warning(
                    f"Ownership percentages don't sum to 100% for terminal: {terminal}",
                    total=total_percentage
                )

            # Cache for 10 minutes (ownership data changes infrequently)
            self.cache.set(cache_key, ownership_data, ttl_seconds=600)

            logger.info(
                f"Retrieved ownership data for terminal: {terminal}",
                partners_count=len(ownership_data),
                total_percentage=round(total_percentage, 2)
            )

            return ownership_data

        except Exception as e:
            logger.error(
                f"Failed to retrieve ownership data for terminal: {terminal}",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
