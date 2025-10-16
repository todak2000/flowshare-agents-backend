"""
Anomaly Detector - Detects statistical anomalies using historical data
KISS principle: Does one thing - statistical anomaly detection
"""
from typing import List
import statistics
import asyncio
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import ProductionEntry, ValidationIssue, SeverityLevel
from shared.config import config
from shared.firestore_client import firestore_client
from shared.logger import logger


class AnomalyDetector:
    """
    Detects statistical anomalies in production data

    Uses z-score analysis to identify volumes that deviate significantly
    from historical patterns for a given partner.

    Single Responsibility: Anomaly detection only
    """

    def __init__(self, cache):
        """
        Initialize anomaly detector

        Args:
            cache: Cache instance for historical data
        """
        self.cache = cache

    async def detect(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """
        Detect anomalies using statistical analysis

        Args:
            entry: Production entry to analyze

        Returns:
            List of validation issues if anomalies detected
        """
        issues = []

        try:
            historical_entries = await self._get_historical_data(entry.partner)

            if len(historical_entries) < config.MIN_HISTORICAL_SAMPLES:
                logger.info(
                    "Insufficient historical data",
                    partner=entry.partner,
                    available_samples=len(historical_entries),
                    required_samples=config.MIN_HISTORICAL_SAMPLES
                )
                return issues

            anomaly_issue = self._analyze_volume_anomaly(entry, historical_entries)
            if anomaly_issue:
                issues.append(anomaly_issue)

        except Exception as e:
            logger.error(
                "Anomaly detection failed",
                partner=entry.partner,
                error=str(e),
                error_type=type(e).__name__
            )

        return issues

    async def _get_historical_data(self, partner: str) -> List[dict]:
        """
        Get historical data for partner (with caching)

        Args:
            partner: Partner name

        Returns:
            List of historical production entries
        """
        cache_key = f"historical_{partner}"

        # Try cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for partner: {partner}")
            return cached_data

        # Cache miss - query Firestore
        logger.debug(f"Cache miss for partner: {partner}, querying Firestore")
        historical_entries = await asyncio.to_thread(
            firestore_client.query_documents,
            collection=config.COLLECTION_PRODUCTION_ENTRIES,
            filters=[
                ('partner', '==', partner),
                ('flagged', '==', False)  # Only use validated data
            ],
            order_by='timestamp',
            limit=30
        )

        # Cache for 5 minutes
        self.cache.set(cache_key, historical_entries, ttl_seconds=300)

        return historical_entries

    def _analyze_volume_anomaly(
        self,
        entry: ProductionEntry,
        historical_entries: List[dict]
    ) -> ValidationIssue | None:
        """
        Analyze if volume is statistically anomalous

        Uses z-score analysis to detect outliers

        Args:
            entry: Current production entry
            historical_entries: Historical data for comparison

        Returns:
            ValidationIssue if anomaly detected, None otherwise
        """
        volumes = [e['gross_volume_bbl'] for e in historical_entries]

        if len(volumes) <= 1:
            return None

        mean = statistics.mean(volumes)
        stdev = statistics.stdev(volumes)

        if stdev == 0:
            return None

        z_score = (entry.gross_volume_bbl - mean) / stdev

        if abs(z_score) <= config.Z_SCORE_THRESHOLD:
            return None

        # Determine severity based on z-score magnitude
        severity = SeverityLevel.HIGH if abs(z_score) > 3.0 else SeverityLevel.MEDIUM

        return ValidationIssue(
            field="gross_volume_bbl",
            severity=severity,
            message=f"Volume {entry.gross_volume_bbl} bbl is {abs(z_score):.2f} standard deviations from average",
            suggestion=f"Historical average: {mean:.2f} bbl (±{stdev:.2f}). Verify meter reading.",
            value=entry.gross_volume_bbl
        )
